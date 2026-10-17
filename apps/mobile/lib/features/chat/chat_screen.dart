import 'package:flutter/material.dart';

import '../sos/sos_screen.dart';

/// Local reply used until the chat is wired to the backend `/v1/messages`.
const String companionUnavailableReply =
    'Gracias por escribirme. Todavía no puedo conversar, pronto estaré '
    'disponible. Si necesitas apoyo ahora, toca Ayuda ahora.';

class ChatMessage {
  const ChatMessage({required this.text, required this.fromUser});

  final String text;
  final bool fromUser;
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, this.launchPhone = launchPhoneWithUrlLauncher});

  final PhoneLauncher launchPhone;

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<ChatMessage> _messages = [];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _send() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    setState(() {
      _messages
        ..add(ChatMessage(text: text, fromUser: true))
        ..add(
          const ChatMessage(text: companionUnavailableReply, fromUser: false),
        );
    });
    _controller.clear();
  }

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
                padding: const EdgeInsets.all(16),
                itemCount: _messages.length,
                itemBuilder: (_, index) =>
                    MessageBubble(message: _messages[index]),
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
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(),
                      decoration: const InputDecoration(
                        hintText: 'Escribe cómo te sientes',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    tooltip: 'Enviar',
                    icon: const Icon(Icons.send),
                    onPressed: _send,
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
