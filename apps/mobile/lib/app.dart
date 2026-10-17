import 'package:flutter/material.dart';

import 'features/chat/chat_screen.dart';
import 'features/sos/sos_screen.dart';

class PuenteApp extends StatelessWidget {
  const PuenteApp({super.key, this.launchPhone = launchPhoneWithUrlLauncher});

  /// Injected so tests never reach the real `url_launcher` plugin.
  final PhoneLauncher launchPhone;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Puente',
      debugShowCheckedModeBanner: false,
      theme: _theme(Brightness.light),
      darkTheme: _theme(Brightness.dark),
      home: ChatScreen(launchPhone: launchPhone),
    );
  }
}

/// Calm, high-contrast Material 3 theme with a soft teal seed.
ThemeData _theme(Brightness brightness) {
  final colors = ColorScheme.fromSeed(
    seedColor: const Color(0xFF4A8C8C),
    brightness: brightness,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: colors,
    visualDensity: VisualDensity.standard,
    materialTapTargetSize: MaterialTapTargetSize.padded,
  );
}
