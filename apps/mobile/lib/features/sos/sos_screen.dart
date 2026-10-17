import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import 'crisis_resources.dart';

/// Opens a `tel:` URI. Returns false when the platform cannot place the call.
typedef PhoneLauncher = Future<bool> Function(Uri uri);

Future<bool> launchPhoneWithUrlLauncher(Uri uri) => launchUrl(uri);

/// AppBar action that opens the SOS screen. It never touches the network.
class SosAction extends StatelessWidget {
  const SosAction({super.key, this.launchPhone = launchPhoneWithUrlLauncher});

  final PhoneLauncher launchPhone;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilledButton.icon(
        style: FilledButton.styleFrom(
          backgroundColor: colors.error,
          foregroundColor: colors.onError,
        ),
        icon: const Icon(Icons.sos),
        label: const Text('Ayuda ahora'),
        onPressed: () => Navigator.of(context).push(
          MaterialPageRoute<void>(
            builder: (_) => SosScreen(launchPhone: launchPhone),
          ),
        ),
      ),
    );
  }
}

class SosScreen extends StatefulWidget {
  const SosScreen({super.key, this.launchPhone = launchPhoneWithUrlLauncher});

  final PhoneLauncher launchPhone;

  @override
  State<SosScreen> createState() => _SosScreenState();
}

class _SosScreenState extends State<SosScreen> {
  /// Resources whose call could not be launched; their number stays visible.
  final Set<String> _failed = {};

  Future<void> _call(CrisisResource resource) async {
    bool launched;
    try {
      launched = await widget.launchPhone(resource.telUri);
    } catch (_) {
      launched = false;
    }
    if (launched || !mounted) return;
    setState(() => _failed.add(resource.id));
    final option = resource.option == null ? '' : ' y luego ${resource.option}';
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'No pudimos abrir el teléfono. Marca ${resource.number}$option '
          'desde tu teléfono.',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    return Scaffold(
      appBar: AppBar(title: const Text('Ayuda ahora')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text(
            'No estás solo. Si estás en peligro, llama ahora.',
            style: textTheme.titleMedium,
          ),
          const SizedBox(height: 16),
          for (final resource in crisisResources)
            _ResourceCard(
              resource: resource,
              showNumber: _failed.contains(resource.id),
              onCall: () => _call(resource),
            ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                communityMentalHealthNote,
                style: textTheme.bodyLarge,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ResourceCard extends StatelessWidget {
  const _ResourceCard({
    required this.resource,
    required this.showNumber,
    required this.onCall,
  });

  final CrisisResource resource;
  final bool showNumber;
  final VoidCallback onCall;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final details = [
      resource.purpose,
      if (resource.free == true) 'Gratuita',
      if (resource.availability != null) resource.availability!,
    ].join(' · ');

    return Card(
      key: ValueKey('resource-${resource.id}'),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(resource.name, style: textTheme.titleLarge),
            const SizedBox(height: 4),
            Text(details, style: textTheme.bodyMedium),
            if (resource.option != null)
              Text(
                'Llama al ${resource.number}, luego marca ${resource.option}.',
                style: textTheme.bodyMedium,
              ),
            if (showNumber) ...[
              const SizedBox(height: 8),
              SelectableText(resource.number, style: textTheme.headlineSmall),
            ],
            const SizedBox(height: 12),
            FilledButton.icon(
              key: ValueKey('call-${resource.id}'),
              icon: const Icon(Icons.call),
              label: Text('Llamar al ${resource.number}'),
              onPressed: onCall,
            ),
          ],
        ),
      ),
    );
  }
}
