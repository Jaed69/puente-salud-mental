import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import 'companion_models.dart';

/// Backend base URL, set with `--dart-define=PUENTE_API_BASE_URL=...`.
/// The default reaches the host machine from the Android emulator.
const String defaultApiBaseUrl = String.fromEnvironment(
  'PUENTE_API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

const Duration defaultApiTimeout = Duration(seconds: 30);

/// Sends a user message to the companion and returns its response.
abstract interface class CompanionApi {
  /// Throws [CompanionUnavailableException] when no valid response arrives.
  Future<CompanionResponse> sendMessage(
    String text, {
    List<HistoryTurn> history,
  });
}

/// The companion could not be reached or answered with an invalid response.
/// Deliberately carries no message text or response body (Ley 29733).
class CompanionUnavailableException implements Exception {
  const CompanionUnavailableException();

  @override
  String toString() => 'CompanionUnavailableException';
}

/// [CompanionApi] over HTTP against `POST /v1/messages`.
class HttpCompanionApi implements CompanionApi {
  const HttpCompanionApi({
    this.baseUrl = defaultApiBaseUrl,
    this.timeout = defaultApiTimeout,
    this.client,
  });

  final String baseUrl;
  final Duration timeout;

  /// Injected in tests. When null, a client is created and closed per request.
  final http.Client? client;

  Uri get _endpoint {
    final base = baseUrl.endsWith('/')
        ? baseUrl.substring(0, baseUrl.length - 1)
        : baseUrl;
    return Uri.parse('$base/v1/messages');
  }

  @override
  Future<CompanionResponse> sendMessage(
    String text, {
    List<HistoryTurn> history = const [],
  }) async {
    final ownClient = client == null;
    final httpClient = client ?? http.Client();
    try {
      final response = await httpClient
          .post(
            _endpoint,
            headers: const {'content-type': 'application/json'},
            body: jsonEncode({
              'text': text,
              'history': [
                for (final turn in boundedHistory(history)) turn.toJson(),
              ],
            }),
          )
          .timeout(timeout);
      if (response.statusCode != 200) {
        throw const CompanionUnavailableException();
      }
      // FastAPI sends JSON without a charset, so decode the bytes as UTF-8
      // explicitly instead of relying on `response.body` (Latin-1 fallback).
      return CompanionResponse.fromJson(
        jsonDecode(utf8.decode(response.bodyBytes)),
      );
    } on CompanionUnavailableException {
      rethrow;
    } on Object {
      // Timeout, network error, invalid UTF-8 or JSON: never surface details.
      throw const CompanionUnavailableException();
    } finally {
      if (ownClient) httpClient.close();
    }
  }
}
