import 'package:flutter/material.dart';

import '../sos/sos_screen.dart';
import 'crisis_card.dart';
import 'data/companion_api.dart';
import 'data/companion_models.dart';

/// Fixed local message shown when the companion cannot answer (timeout,
/// network error, invalid response). It never depends on the backend.
const String companionUnavailableReply =
    'En este momento no puedo responderte. Si necesitas apoyo ahora, llama '
    'gratis a la Línea 113, opción 5, o toca Ayuda ahora.';

/// One item in the conversation.
sealed class ChatEntry {
  const ChatEntry();
}

/// A user message or a companion reply, rendered as a bubble.
class ChatMessage extends ChatEntry {
  const ChatMessage({required this.text, required this.fromUser});

  final String text;
  final bool fromUser;
}

/// A crisis response, rendered as a [CrisisCard].
class CrisisEntry extends ChatEntry {
  const CrisisEntry(this.crisis);

  final CompanionCrisis crisis;
}

/// The local fallback after a failed request. Never sent back as history.
class UnavailableEntry extends ChatEntry {
  const UnavailableEntry();
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({
    super.key,
    this.companionApi = const HttpCompanionApi(),
    this.launchPhone = launchPhoneWithUrlLauncher,
  });

  final CompanionApi companionApi;
  final PhoneLauncher launchPhone;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scroll = ScrollController();
  final List<ChatEntry> _entries = [];
  bool _sending = false;

  @override
  void dispose() {
    _controller.dispose();
    _scroll.dispose();
    super.dispose();
  }

  /// Earlier turns as context for the companion, oldest first. Local fallback
  /// entries are skipped; a crisis counts as an assistant turn.
  List<HistoryTurn> _history() {
    final turns = <HistoryTurn>[];
    for (final entry in _entries) {
      final turn = switch (entry) {
        ChatMessage(:final text, :final fromUser) => HistoryTurn(
          role: fromUser ? HistoryRole.user : HistoryRole.assistant,
          text: text,
        ),
        CrisisEntry(:final crisis) => HistoryTurn(
          role: HistoryRole.assistant,
          text: crisis.message,
        ),
        UnavailableEntry() => null,
      };
      // The backend rejects turns over its length limit; skip them.
      if (turn != null && turn.text.length <= maxMessageLength) {
        turns.add(turn);
      }
    }
    return boundedHistory(turns);
  }

  Future<void> _send() async {
    if (_sending) return;
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    final history = _history();
    setState(() {
      _entries.add(ChatMessage(text: text, fromUser: true));
      _sending = true;
    });
    _controller.clear();
    _scrollToEnd();

    ChatEntry answer;
    try {
      final response = await widget.companionApi.sendMessage(
        text,
        history: history,
      );
      answer = switch (response) {
        CompanionReply(:final message) => ChatMessage(
          text: message,
          fromUser: false,
        ),
        CompanionCrisis crisis => CrisisEntry(crisis),
      };
    } catch (_) {
      // Never crash and never log the content: show the local fallback.
      answer = const UnavailableEntry();
    }
    if (!mounted) return;
    setState(() {
      _entries.add(answer);
      _sending = false;
    });
    _scrollToEnd();
  }

  void _scrollToEnd() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scroll.hasClients) return;
      _scroll.animateTo(
        _scroll.position.maxScrollExtent,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
      );
    });
  }

  Widget _buildEntry(ChatEntry entry) => switch (entry) {
    ChatMessage message => MessageBubble(message: message),
    CrisisEntry(:final crisis) => CrisisCard(
      crisis: crisis,
      launchPhone: widget.launchPhone,
    ),
    UnavailableEntry() => CompanionUnavailableCard(
      launchPhone: widget.launchPhone,
    ),
  };

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Puente'),
        actions: [SosAction(launchPhone: widget.launchPhone)],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Container(
              width: double.infinity,
              color: colors.secondaryContainer,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(
                'Puente no reemplaza a un profesional. '
                'Si estás en peligro, toca Ayuda ahora.',
                style: TextStyle(color: colors.onSecondaryContainer),
              ),
            ),
            Expanded(
              child: ListView.builder(
                controller: _scroll,
                padding: const EdgeInsets.all(16),
                itemCount: _entries.length + (_sending ? 1 : 0),
                itemBuilder: (_, index) => index < _entries.length
                    ? _buildEntry(_entries[index])
                    : const TypingIndicator(),
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 8, 16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      minLines: 1,
                      maxLines: 4,
                      maxLength: maxMessageLength,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(),
                      decoration: const InputDecoration(
                        hintText: 'Escribe cómo te sientes',
                        border: OutlineInputBorder(),
                        counterText: '',
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    tooltip: 'Enviar',
                    icon: const Icon(Icons.send),
                    onPressed: _sending ? null : _send,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class MessageBubble extends StatelessWidget {
  const MessageBubble({super.key, required this.message});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final fromUser = message.fromUser;
    return Align(
      alignment: fromUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 480),
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: fromUser
              ? colors.primaryContainer
              : colors.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          message.text,
          style: TextStyle(
            color: fromUser ? colors.onPrimaryContainer : colors.onSurface,
          ),
        ),
      ),
    );
  }
}

/// Shown while the companion is answering.
class TypingIndicator extends StatelessWidget {
  const TypingIndicator({super.key});

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Align(
      key: const ValueKey('typing-indicator'),
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: colors.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox.square(
              dimension: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            const SizedBox(width: 8),
            Text('Escribiendo…', style: TextStyle(color: colors.onSurface)),
          ],
        ),
      ),
    );
  }
}

/// Local fallback when the companion is not available. Opens the SOS screen,
/// which works offline.
class CompanionUnavailableCard extends StatelessWidget {
  const CompanionUnavailableCard({super.key, required this.launchPhone});

  final PhoneLauncher launchPhone;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 480),
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: colors.surfaceContainerHigh,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              companionUnavailableReply,
              style: TextStyle(color: colors.onSurface),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              key: const ValueKey('fallback-open-sos'),
              icon: const Icon(Icons.sos),
              label: const Text('Ver líneas de ayuda'),
              onPressed: () => openSosScreen(context, launchPhone),
            ),
          ],
        ),
      ),
    );
  }
}
