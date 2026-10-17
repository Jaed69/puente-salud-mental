import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:puente/app.dart';
import 'package:puente/features/sos/crisis_resources.dart';
import 'package:puente/features/sos/sos_screen.dart';

/// Records every URI the SOS screen asks to launch, without touching the
/// platform `url_launcher` plugin.
class FakeLauncher {
  FakeLauncher({this.succeeds = true});

  final bool succeeds;
  final List<Uri> launched = [];

  Future<bool> call(Uri uri) async {
    launched.add(uri);
    return succeeds;
  }
}

void useTallViewport(WidgetTester tester) {
  tester.view.physicalSize = const Size(800, 2400);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
}

Future<void> pumpSos(WidgetTester tester, FakeLauncher launcher) async {
  useTallViewport(tester);
  await tester.pumpWidget(
    MaterialApp(home: SosScreen(launchPhone: launcher.call)),
  );
}

void main() {
  group('SOS action', () {
    testWidgets('is visible on the chat screen', (tester) async {
      await tester.pumpWidget(PuenteApp(launchPhone: FakeLauncher().call));

      expect(find.text('Ayuda ahora'), findsOneWidget);
    });

    testWidgets('opens the SOS screen', (tester) async {
      useTallViewport(tester);
      await tester.pumpWidget(PuenteApp(launchPhone: FakeLauncher().call));

      await tester.tap(find.text('Ayuda ahora'));
      await tester.pumpAndSettle();

      expect(find.byType(SosScreen), findsOneWidget);
    });
  });

  group('SOS screen', () {
    test('lists Linea 113 opcion 5 first and the five Peru resources', () {
      expect(crisisResources.first.id, 'minsa_113_5');
      expect(crisisResources.first.number, '113');
      expect(crisisResources.first.option, '5');
      expect(crisisResources.map((r) => r.number), [
        '113',
        '106',
        '105',
        '116',
        '100',
      ]);
    });

    test('only Linea 113 opcion 5 is marked verified, like the backend', () {
      expect(crisisResources.where((r) => r.verified).map((r) => r.id), [
        'minsa_113_5',
      ]);
    });

    testWidgets('renders all five resources with 113 opcion 5 on top', (
      tester,
    ) async {
      await pumpSos(tester, FakeLauncher());

      for (final resource in crisisResources) {
        expect(find.text(resource.name), findsOneWidget);
      }
      final first = tester.getTopLeft(find.text('Línea 113, opción 5')).dy;
      for (final resource in crisisResources.skip(1)) {
        expect(
          tester.getTopLeft(find.text(resource.name)).dy,
          greaterThan(first),
        );
      }
      expect(find.textContaining('luego marca 5'), findsOneWidget);
    });

    testWidgets('shows the community mental health centre note', (
      tester,
    ) async {
      await pumpSos(tester, FakeLauncher());

      expect(
        find.textContaining('Centro de Salud Mental Comunitario'),
        findsOneWidget,
      );
    });

    testWidgets('call button dials tel:113 for Linea 113 opcion 5', (
      tester,
    ) async {
      final launcher = FakeLauncher();
      await pumpSos(tester, launcher);

      await tester.tap(find.byKey(const ValueKey('call-minsa_113_5')));
      await tester.pump();

      expect(launcher.launched, [Uri(scheme: 'tel', path: '113')]);
    });

    testWidgets('failed launch shows the number and a SnackBar', (
      tester,
    ) async {
      await pumpSos(tester, FakeLauncher(succeeds: false));

      await tester.tap(find.byKey(const ValueKey('call-samu_106')));
      await tester.pump();

      expect(find.byType(SnackBar), findsOneWidget);
      expect(
        find.byWidgetPredicate((w) => w is SelectableText && w.data == '106'),
        findsOneWidget,
      );
    });

    testWidgets('a launcher that throws is handled like a failure', (
      tester,
    ) async {
      useTallViewport(tester);
      await tester.pumpWidget(
        MaterialApp(
          home: SosScreen(launchPhone: (_) async => throw Exception('boom')),
        ),
      );

      await tester.tap(find.byKey(const ValueKey('call-pnp_105')));
      await tester.pump();

      expect(find.byType(SnackBar), findsOneWidget);
    });
  });
}
