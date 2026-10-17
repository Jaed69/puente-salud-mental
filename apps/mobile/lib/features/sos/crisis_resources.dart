// Peru crisis resources, bundled as local constants so the SOS screen works
// with no network. Mirrors `apps/backend/src/puente/guardian/resources.py`.
//
// Only Linea 113 opcion 5 is verified (press citing MINSA, 2025). Every other
// number is pending official confirmation (same as the backend `verified`
// flags) and must be reviewed against gob.pe or the owning institution before
// any real user sees this screen. WhatsApp or chat channels are intentionally
// absent: none has been verified.

class CrisisResource {
  const CrisisResource({
    required this.id,
    required this.name,
    required this.number,
    required this.organization,
    required this.purpose,
    required this.verified,
    this.option,
    this.availability,
    this.free,
    this.source,
  });

  final String id;
  final String name;

  /// The number to dial. For menu-based lines, [option] is pressed after the
  /// call connects.
  final String number;
  final String? option;
  final String organization;
  final String purpose;
  final String? availability;
  final bool? free;
  final bool verified;

  /// Where the entry was confirmed, or why it is still pending.
  final String? source;

  Uri get telUri => Uri(scheme: 'tel', path: number);
}

const List<CrisisResource> crisisResources = [
  CrisisResource(
    id: 'minsa_113_5',
    name: 'Línea 113, opción 5',
    number: '113',
    option: '5',
    organization: 'MINSA',
    purpose: 'Apoyo en salud mental',
    availability: '24/7',
    free: true,
    verified: true,
  ),
  CrisisResource(
    id: 'samu_106',
    name: 'SAMU 106',
    number: '106',
    organization: 'MINSA - SAMU',
    purpose: 'Emergencias médicas',
    verified: false,
  ),
  CrisisResource(
    id: 'pnp_105',
    name: 'Policía Nacional 105',
    number: '105',
    organization: 'PNP',
    purpose: 'Peligro inmediato o violencia',
    verified: false,
  ),
  CrisisResource(
    id: 'bomberos_116',
    name: 'Bomberos 116',
    number: '116',
    organization: 'Cuerpo General de Bomberos Voluntarios del Perú',
    purpose: 'Emergencias y rescate',
    verified: false,
  ),
  CrisisResource(
    id: 'mimp_100',
    name: 'Línea 100',
    number: '100',
    organization: 'MIMP',
    purpose: 'Orientación ante violencia familiar o sexual',
    verified: false,
  ),
];

/// A short note shown with the crisis resources, with its source.
class ResourceNote {
  const ResourceNote({required this.text, required this.source});

  final String text;
  final String source;
}

/// Source: https://www.gob.pe/10942
const String communityMentalHealthNote =
    'Si estás en riesgo de suicidio, puedes acudir directamente a un Centro '
    'de Salud Mental Comunitario, sin referencia.';

const ResourceNote communityMentalHealthResourceNote = ResourceNote(
  text: communityMentalHealthNote,
  source: 'https://www.gob.pe/10942',
);
