import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:puente/features/chat/data/companion_api.dart';
import 'package:puente/features/chat/data/companion_models.dart';
import 'package:puente/features/sos/crisis_resources.dart';

const Map<String, Object?> crisisJson = {
  'type': 'crisis',
  'message': 'No tienes que pasar por esto a solas.',
  'resources': [
    {
      'id': 'minsa_113_5',
      'name': 'Línea 113, opción 5',
      'number': '113',
      'option': '5',
      'organization': 'MINSA',
      'purpose': 'Apoyo en salud mental',
      'availability': '24/7',
      'free': true,
      'verified': true,
      'source': 'Press citing MINSA, 2025.',
    },
    {
      'id': 'samu_106',
      'name': 'SAMU 106',
      'number': '106',
      'option': null,
      'organization': 'MINSA - SAMU',
      'purpose': 'Emergencias médicas',
      'availability': null,
      'free': null,
      'verified': false,
      'source': 'Pending confirmation.',
    },
  ],
  'note': {
    'text': 'Puedes acudir a un Centro de Salud Mental Comunitario.',
    'source': 'https://www.gob.pe/10942',
  },
};

http.Response jsonResponse(Object body, {int status = 200}) => http.Response(
  jsonEncode(body),
  status,
  headers: {'content-type': 'application/json'},
);

void main() {
  group('CompanionResponse.fromJson', () {
    test('parses a reply', () {
      final response = CompanionResponse.fromJson({
        'type': 'reply',
        'message': 'Te escucho.',
      });

      expect(response, isA<CompanionReply>());
      expect(response.message, 'Te escucho.');
    });

    test('parses a crisis with its resources and note', () {
      final response = CompanionResponse.fromJson(crisisJson);

      expect(response, isA<CompanionCrisis>());
      final crisis = response as CompanionCrisis;
      expect(crisis.message, 'No tienes que pasar por esto a solas.');
      expect(crisis.resources.map((r) => r.id), ['minsa_113_5', 'samu_106']);
      final first = crisis.resources.first;
      expect(first.number, '113');
      expect(first.option, '5');
      expect(first.free, isTrue);
      expect(first.verified, isTrue);
      expect(first.availability, '24/7');
      expect(first.source, 'Press citing MINSA, 2025.');
      expect(crisis.resources.last.option, isNull);
      expect(crisis.resources.last.free, isNull);
      expect(crisis.note.text, contains('Centro de Salud Mental Comunitario'));
      expect(crisis.note.source, 'https://www.gob.pe/10942');
    });

    for (final malformed in <Object?>[
      null,
      'reply',
      <String, Object?>{},
      {'type': 'reply'},
      {'type': 'reply', 'message': ''},
      {'type': 'reply', 'message': 42},
      {'type': 'unknown', 'message': 'Hola'},
    ]) {
      test('rejects malformed payload $malformed', () {
        expect(
          () => CompanionResponse.fromJson(malformed),
          throwsFormatException,
        );
      });
    }

    test('a malformed crisis fails closed to the local crisis resources', () {
      final response = CompanionResponse.fromJson({
        'type': 'crisis',
        'message': 'No estás solo.',
        'resources': [
          {'id': 'broken'},
        ],
      });

      expect(response, isA<CompanionCrisis>());
      final crisis = response as CompanionCrisis;
      expect(crisis.message, isNotEmpty);
      expect(crisis.resources, crisisResources);
      expect(crisis.note.text, communityMentalHealthNote);
    });

    test('a crisis with no resources fails closed to the local ones', () {
      final response = CompanionResponse.fromJson({
        'type': 'crisis',
        'message': 'No estás solo.',
        'resources': <Object?>[],
        'note': {'text': 'Nota', 'source': 'x'},
      });

      expect((response as CompanionCrisis).resources, crisisResources);
    });
  });

  group('boundedHistory', () {
    test('keeps the last 10 turns in order', () {
      final turns = [
        for (var i = 0; i < 13; i++)
          HistoryTurn(
            role: i.isEven ? HistoryRole.user : HistoryRole.assistant,
            text: 'turn $i',
          ),
      ];

      final bounded = boundedHistory(turns);

      expect(bounded.map((t) => t.text), [
        for (var i = 3; i < 13; i++) 'turn $i',
      ]);
    });
  });

  group('HttpCompanionApi', () {
    test('posts text and history as JSON to /v1/messages', () async {
      late http.Request sent;
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test:8000',
        client: MockClient((request) async {
          sent = request;
          return jsonResponse({'type': 'reply', 'message': 'Hola'});
        }),
      );

      await api.sendMessage(
        'Me siento solo',
        history: const [
          HistoryTurn(role: HistoryRole.user, text: 'Hola'),
          HistoryTurn(role: HistoryRole.assistant, text: 'Te escucho'),
        ],
      );

      expect(sent.method, 'POST');
      expect(sent.url, Uri.parse('http://example.test:8000/v1/messages'));
      expect(sent.headers['content-type'], startsWith('application/json'));
      expect(jsonDecode(sent.body), {
        'text': 'Me siento solo',
        'history': [
          {'role': 'user', 'text': 'Hola'},
          {'role': 'assistant', 'text': 'Te escucho'},
        ],
      });
    });

    test('sends at most 10 history turns', () async {
      late http.Request sent;
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test',
        client: MockClient((request) async {
          sent = request;
          return jsonResponse({'type': 'reply', 'message': 'Hola'});
        }),
      );

      await api.sendMessage(
        'Hola',
        history: [
          for (var i = 0; i < 15; i++)
            HistoryTurn(role: HistoryRole.user, text: 'turn $i'),
        ],
      );

      final history = (jsonDecode(sent.body) as Map)['history'] as List;
      expect(history.map((t) => (t as Map)['text']), [
        for (var i = 5; i < 15; i++) 'turn $i',
      ]);
    });

    test('decodes UTF-8 bodies without a charset header', () async {
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test',
        client: MockClient(
          (_) async => http.Response.bytes(
            utf8.encode(jsonEncode({'type': 'reply', 'message': 'Línea'})),
            200,
            headers: {'content-type': 'application/json'},
          ),
        ),
      );

      final response = await api.sendMessage('Hola');

      expect(response.message, 'Línea');
    });

    test('parses a crisis response', () async {
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test',
        client: MockClient((_) async => jsonResponse(crisisJson)),
      );

      final response = await api.sendMessage('Hola');

      expect(response, isA<CompanionCrisis>());
    });

    test('a non-200 status is unavailable', () async {
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test',
        client: MockClient(
          (_) async => jsonResponse({'detail': []}, status: 422),
        ),
      );

      expect(
        api.sendMessage('Hola'),
        throwsA(isA<CompanionUnavailableException>()),
      );
    });

    test('malformed JSON is unavailable', () async {
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test',
        client: MockClient((_) async => http.Response('<html>', 200)),
      );

      expect(
        api.sendMessage('Hola'),
        throwsA(isA<CompanionUnavailableException>()),
      );
    });

    test('a network error is unavailable', () async {
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test',
        client: MockClient((_) async => throw http.ClientException('offline')),
      );

      expect(
        api.sendMessage('Hola'),
        throwsA(isA<CompanionUnavailableException>()),
      );
    });

    test('a timeout is unavailable', () async {
      final api = HttpCompanionApi(
        baseUrl: 'http://example.test',
        timeout: const Duration(milliseconds: 10),
        client: MockClient((_) => Completer<http.Response>().future),
      );

      expect(
        api.sendMessage('Hola'),
        throwsA(isA<CompanionUnavailableException>()),
      );
    });
  });
}
