import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:puente/features/chat/chat_screen.dart';

Future<void> pumpChat(WidgetTester tester) async {
  await tester.pumpWidget(
    MaterialApp(home: ChatScreen(launchPhone: (_) async => true)),
  );
}

void main() {
  testWidgets('shows the safety disclaimer', (tester) async {
    await pumpChat(tester);

    expect(
      find.text(
        'Puente no reemplaza a un profesional. '
        'Si estás en peligro, toca Ayuda ahora.',
      ),
      findsOneWidget,
    );
  });

  testWidgets('sending appends the message and the placeholder reply', (
    tester,
  ) async {
    await pumpChat(tester);

    await tester.enterText(find.byType(TextField), 'Hoy me siento cansado');
    await tester.tap(find.byTooltip('Enviar'));
    await tester.pump();

    expect(find.text('Hoy me siento cansado'), findsOneWidget);
    expect(find.text(companionUnavailableReply), findsOneWidget);
    final field = tester.widget<TextField>(find.byType(TextField));
    expect(field.controller!.text, isEmpty);
  });

  testWidgets('empty or blank input does not send', (tester) async {
    await pumpChat(tester);

    await tester.tap(find.byTooltip('Enviar'));
    await tester.pump();
    await tester.enterText(find.byType(TextField), '   ');
    await tester.tap(find.byTooltip('Enviar'));
    await tester.pump();

    expect(find.byType(MessageBubble), findsNothing);
    expect(find.text(companionUnavailableReply), findsNothing);
  });
}
