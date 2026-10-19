import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:puente/features/chat/chat_screen.dart';
import 'package:puente/features/chat/crisis_card.dart';
import 'package:puente/features/chat/data/companion_api.dart';
import 'package:puente/features/chat/data/companion_models.dart';
import 'package:puente/features/sos/crisis_resources.dart';
import 'package:puente/features/sos/sos_screen.dart';

typedef Handler = Future<CompanionResponse> Function(
  String text,
  List<HistoryTurn> history,
);

/// In-memory [CompanionApi]: records each call and never touches the network.
class FakeCompanionApi implements CompanionApi {
  FakeCompanionApi(this.handler);

  FakeCompanionApi.replying(String reply)
    : handler = ((_, _) async => CompanionReply(reply));

  final Handler handler;
  final List<({String text, List<HistoryTurn> history})> calls = [];

  @override
  Future<CompanionResponse> sendMessage(
    String text, {
    List<HistoryTurn> history = const [],
  }) {
    calls.add((text: text, history: List.of(history)));
    return handler(text, history);
  }
}

class FakeLauncher {
  final List<Uri> launched = [];

  Future<bool> call(Uri uri) async {
    launched.add(uri);
    return true;
  }
}

final CompanionCrisis sampleCrisis = CompanionCrisis(
  message: 'No tienes que pasar por esto a solas.',
  resources: crisisResources.take(2).toList(),
  note: const ResourceNote(
    text: 'Puedes acudir a un Centro de Salud Mental Comunitario.',
    source: 'https://www.gob.pe/10942',
  ),
);

void useTallViewport(WidgetTester tester) {
  tester.view.physicalSize = const Size(800, 2400);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
}

Future<void> pumpChat(
  WidgetTester tester,
  CompanionApi api, {
  FakeLauncher? launcher,
}) async {
  useTallViewport(tester);
  await tester.pumpWidget(
    MaterialApp(
      home: ChatScreen(
        companionApi: api,
        launchPhone: (launcher ?? FakeLauncher()).call,
      ),
    ),
  );
}

Future<void> sendText(WidgetTester tester, String text) async {
  await tester.enterText(find.byType(TextField), text);
  await tester.tap(find.byTooltip('Enviar'));
  await tester.pump();
}

IconButton sendButton(WidgetTester tester) =>
    tester.widget<IconButton>(find.widgetWithIcon(IconButton, Icons.send));

void main() {
  testWidgets('shows the safety disclaimer', (tester) async {
    await pumpChat(tester, FakeCompanionApi.replying('Hola'));

    expect(
      find.text(
        'Puente no reemplaza a un profesional. '
        'Si estás en peligro, toca Ayuda ahora.',
      ),
      findsOneWidget,
    );
  });

  testWidgets('renders the companion reply as an assistant bubble', (
    tester,
  ) async {
    final api = FakeCompanionApi.replying('Te escucho. ¿Qué pasó hoy?');
    await pumpChat(tester, api);

    await sendText(tester, 'Hoy me siento cansado');
    await tester.pumpAndSettle();

    expect(api.calls.single.text, 'Hoy me siento cansado');
    expect(find.text('Hoy me siento cansado'), findsOneWidget);
    expect(find.text('Te escucho. ¿Qué pasó hoy?'), findsOneWidget);
    expect(find.byType(MessageBubble), findsNWidgets(2));
    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.controller!.text, isEmpty);
  });

  testWidgets('empty or blank input does not send', (tester) async {
    final api = FakeCompanionApi.replying('Hola');
    await pumpChat(tester, api);

    await tester.tap(find.byTooltip('Enviar'));
    await tester.pump();
    await sendText(tester, '   ');

    expect(api.calls, isEmpty);
    expect(find.byType(MessageBubble), findsNothing);
  });

  testWidgets('shows a typing indicator and disables sending while pending', (
    tester,
  ) async {
    final pending = Completer<CompanionResponse>();
    final api = FakeCompanionApi((_, _) => pending.future);
    await pumpChat(tester, api);

    await sendText(tester, 'Hola');

    expect(find.byKey(const ValueKey('typing-indicator')), findsOneWidget);
    expect(sendButton(tester).onPressed, isNull);

    await tester.enterText(find.byType(TextField), 'Otro mensaje');
    await tester.testTextInput.receiveAction(TextInputAction.send);
    await tester.pump();
    expect(api.calls, hasLength(1));

    pending.complete(const CompanionReply('Aquí estoy'));
    await tester.pumpAndSettle();

    expect(find.byKey(const ValueKey('typing-indicator')), findsNothing);
    expect(sendButton(tester).onPressed, isNotNull);
    expect(find.text('Aquí estoy'), findsOneWidget);
  });

  testWidgets('sends the last 10 turns as history, oldest first', (
    tester,
  ) async {
    final api = FakeCompanionApi((text, _) async => CompanionReply('r:$text'));
    await pumpChat(tester, api);

    for (var i = 0; i < 7; i++) {
      await sendText(tester, 'm$i');
      await tester.pumpAndSettle();
    }

    expect(api.calls.first.history, isEmpty);
    final last = api.calls.last;
    expect(last.text, 'm6');
    expect(last.history, hasLength(10));
    expect(last.history.map((t) => t.text), [
      'm1',
      'r:m1',
      'm2',
      'r:m2',
      'm3',
      'r:m3',
      'm4',
      'r:m4',
      'm5',
      'r:m5',
    ]);
    expect(last.history.map((t) => t.role), [
      for (var i = 0; i < 5; i++) ...[HistoryRole.user, HistoryRole.assistant],
    ]);
  });

  testWidgets('renders a crisis card with resources and the note', (
    tester,
  ) async {
    await pumpChat(tester, FakeCompanionApi((_, _) async => sampleCrisis));

    await sendText(tester, 'mensaje');
    await tester.pumpAndSettle();

    expect(find.byType(CrisisCard), findsOneWidget);
    expect(find.text(sampleCrisis.message), findsOneWidget);
    expect(find.text('Línea 113, opción 5'), findsOneWidget);
    expect(find.text('SAMU 106'), findsOneWidget);
    expect(find.textContaining('luego marca 5'), findsOneWidget);
    expect(find.text(sampleCrisis.note.text), findsOneWidget);
  });

  testWidgets('tapping a crisis resource dials it through the launcher', (
    tester,
  ) async {
    final launcher = FakeLauncher();
    await pumpChat(
      tester,
      FakeCompanionApi((_, _) async => sampleCrisis),
      launcher: launcher,
    );

    await sendText(tester, 'mensaje');
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('call-minsa_113_5')));
    await tester.pump();

    expect(launcher.launched, [Uri(scheme: 'tel', path: '113')]);
  });

  testWidgets('the crisis card opens the SOS screen', (tester) async {
    await pumpChat(tester, FakeCompanionApi((_, _) async => sampleCrisis));

    await sendText(tester, 'mensaje');
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('crisis-open-sos')));
    await tester.pumpAndSettle();

    expect(find.byType(SosScreen), findsOneWidget);
  });

  testWidgets('a failure shows the local fallback and keeps the chat usable', (
    tester,
  ) async {
    var fail = true;
    final api = FakeCompanionApi((_, _) async {
      if (fail) throw const CompanionUnavailableException();
      return const CompanionReply('De vuelta');
    });
    await pumpChat(tester, api);

    await sendText(tester, 'Hola');
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.text(companionUnavailableReply), findsOneWidget);
    expect(companionUnavailableReply, contains('Línea 113, opción 5'));
    expect(sendButton(tester).onPressed, isNotNull);

    fail = false;
    await sendText(tester, 'Otra vez');
    await tester.pumpAndSettle();
    expect(find.text('De vuelta'), findsOneWidget);
    // The fallback is local UI, never sent back to the companion as history.
    expect(api.calls.last.history.map((t) => t.text), ['Hola']);
  });

  testWidgets('an unexpected error also shows the fallback', (tester) async {
    await pumpChat(
      tester,
      FakeCompanionApi((_, _) async => throw StateError('x')),
    );

    await sendText(tester, 'Hola');
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.text(companionUnavailableReply), findsOneWidget);
  });

  testWidgets('the fallback opens the SOS screen', (tester) async {
    await pumpChat(
      tester,
      FakeCompanionApi(
        (_, _) async => throw const CompanionUnavailableException(),
      ),
    );

    await sendText(tester, 'Hola');
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const ValueKey('fallback-open-sos')));
    await tester.pumpAndSettle();

    expect(find.byType(SosScreen), findsOneWidget);
  });
}
