// Typed models for the backend `POST /v1/messages` contract
// (`apps/backend/src/puente/api/messages.py`).
//
// Message text is sensitive personal data (Peru Ley 29733): nothing here logs
// it, and error messages never include it.

import '../../sos/crisis_resources.dart';

/// Backend limit on history turns sent with each message.
const int maxHistoryTurns = 10;

/// Backend limit on the length of one message or history turn.
const int maxMessageLength = 4000;

/// Local crisis message used when a crisis response arrives malformed.
const String localCrisisMessage =
    'No tienes que pasar por esto a solas. Llama ahora a la Línea 113, '
    'opción 5: es gratuita y atiende las 24 horas. Si estás en peligro '
    'inmediato, llama al 106 (SAMU).';

enum HistoryRole { user, assistant }

/// One earlier turn of the conversation, sent as context.
class HistoryTurn {
  const HistoryTurn({required this.role, required this.text});

  final HistoryRole role;
  final String text;

  Map<String, Object?> toJson() => {'role': role.name, 'text': text};
}

/// The last [maxHistoryTurns] turns, oldest first.
List<HistoryTurn> boundedHistory(List<HistoryTurn> turns) =>
    turns.length <= maxHistoryTurns
    ? List.of(turns)
    : turns.sublist(turns.length - maxHistoryTurns);

/// A response from the companion: either a [CompanionReply] or a
/// [CompanionCrisis].
sealed class CompanionResponse {
  const CompanionResponse();

  String get message;

  /// Parses a decoded JSON body. Throws [FormatException] when it is not a
  /// valid reply. A crisis that arrives malformed never throws: it fails
  /// closed to the bundled local crisis resources.
  factory CompanionResponse.fromJson(Object? json) {
    if (json is! Map<String, Object?>) {
      throw const FormatException('Response is not a JSON object.');
    }
    return switch (json['type']) {
      'reply' => CompanionReply(_requireText(json['message'])),
      'crisis' => _parseCrisis(json),
      _ => throw const FormatException('Unknown response type.'),
    };
  }
}

final class CompanionReply extends CompanionResponse {
  const CompanionReply(this.message);

  @override
  final String message;
}

final class CompanionCrisis extends CompanionResponse {
  const CompanionCrisis({
    required this.message,
    required this.resources,
    required this.note,
  });

  /// Crisis built only from bundled constants, for when the server payload
  /// cannot be trusted.
  const CompanionCrisis.local()
    : message = localCrisisMessage,
      resources = crisisResources,
      note = communityMentalHealthResourceNote;

  @override
  final String message;
  final List<CrisisResource> resources;
  final ResourceNote note;
}

CompanionCrisis _parseCrisis(Map<String, Object?> json) {
  try {
    final rawResources = json['resources'];
    if (rawResources is! List || rawResources.isEmpty) {
      throw const FormatException('Crisis without resources.');
    }
    final note = json['note'];
    if (note is! Map<String, Object?>) {
      throw const FormatException('Crisis without a note.');
    }
    return CompanionCrisis(
      message: _requireText(json['message']),
      resources: [for (final raw in rawResources) _parseResource(raw)],
      note: ResourceNote(
        text: _requireText(note['text']),
        source: _requireText(note['source']),
      ),
    );
  } on Object {
    // Fail closed: a crisis is always shown, with the local resources.
    return const CompanionCrisis.local();
  }
}

CrisisResource _parseResource(Object? raw) {
  if (raw is! Map<String, Object?>) {
    throw const FormatException('Resource is not a JSON object.');
  }
  final verified = raw['verified'];
  if (verified is! bool) {
    throw const FormatException('Resource without verified flag.');
  }
  return CrisisResource(
    id: _requireText(raw['id']),
    name: _requireText(raw['name']),
    number: _requireText(raw['number']),
    option: _optionalText(raw['option']),
    organization: _requireText(raw['organization']),
    purpose: _requireText(raw['purpose']),
    availability: _optionalText(raw['availability']),
    free: _optionalBool(raw['free']),
    verified: verified,
    source: _optionalText(raw['source']),
  );
}

String _requireText(Object? value) {
  if (value is String && value.trim().isNotEmpty) return value;
  throw const FormatException('Expected a non-empty string.');
}

String? _optionalText(Object? value) {
  if (value == null) return null;
  if (value is String) return value;
  throw const FormatException('Expected a string or null.');
}

bool? _optionalBool(Object? value) {
  if (value == null || value is bool) return value as bool?;
  throw const FormatException('Expected a bool or null.');
}
