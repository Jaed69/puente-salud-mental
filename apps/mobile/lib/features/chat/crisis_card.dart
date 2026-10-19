import 'package:flutter/material.dart';

import '../sos/sos_screen.dart';
import 'data/companion_models.dart';

/// Prominent card for a crisis response: the message, every resource with
/// tap-to-call, the note and a way into the SOS screen.
class CrisisCard extends StatefulWidget {
  const CrisisCard({
    super.key,
    required this.crisis,
    required this.launchPhone,
  });

  final CompanionCrisis crisis;
  final PhoneLauncher launchPhone;

  @override
  State<CrisisCard> createState() => _CrisisCardState();
}

class _CrisisCardState extends State<CrisisCard> {
  /// Resources whose call could not be launched; their number stays visible.
  final Set<String> _failed = {};

  Future<void> _call(String id) async {
    final resource = widget.crisis.resources.firstWhere((r) => r.id == id);
    final launched = await callResource(context, widget.launchPhone, resource);
    if (launched || !mounted) return;
    setState(() => _failed.add(id));
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;
    return Card(
      key: const ValueKey('crisis-card'),
      color: colors.errorContainer,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(Icons.favorite, color: colors.onErrorContainer),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    widget.crisis.message,
                    style: textTheme.titleMedium?.copyWith(
                      color: colors.onErrorContainer,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            for (final resource in widget.crisis.resources)
              ResourceCard(
                resource: resource,
                showNumber: _failed.contains(resource.id),
                onCall: () => _call(resource.id),
              ),
            const SizedBox(height: 8),
            Text(
              widget.crisis.note.text,
              style: textTheme.bodyMedium?.copyWith(
                color: colors.onErrorContainer,
              ),
            ),
            const SizedBox(height: 12),
            FilledButton.icon(
              key: const ValueKey('crisis-open-sos'),
              style: FilledButton.styleFrom(
                backgroundColor: colors.error,
                foregroundColor: colors.onError,
              ),
              icon: const Icon(Icons.sos),
              label: const Text('Ver todas las líneas de ayuda'),
              onPressed: () => openSosScreen(context, widget.launchPhone),
            ),
          ],
        ),
      ),
    );
  }
}
