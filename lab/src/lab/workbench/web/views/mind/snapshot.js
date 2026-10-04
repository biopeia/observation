import { snap } from './state.js';

const LEGACY_OBSERVER_FIELDS = [
  'activationClasses',
  'predictionErrors',
  'activationValues',
  'predictionErrorValues',
];

function firstPresent(source, keys) {
  for (const key of keys) {
    if (Object.hasOwn(source, key)) return { present: true, value: source[key] };
  }
  return { present: false, value: undefined };
}

function availabilityFor(present, value) {
  if (!present) return 'not_observed';
  if (value === null) return 'observed_null';
  if (Array.isArray(value) && value.length === 0) return 'observed_empty';
  return 'observed';
}

function scalar(source, availability, name, ...keys) {
  const found = firstPresent(source, keys);
  availability[name] = availabilityFor(found.present, found.value);
  return found.present ? found.value : null;
}

function collection(source, availability, name, ...keys) {
  const found = firstPresent(source, keys);
  availability[name] = availabilityFor(found.present, found.value);
  // Keep renderers type-stable while retaining the epistemic distinction in
  // snap.availability. [] is presentation storage here, not a claim that the
  // organism reported an empty collection.
  return Array.isArray(found.value) ? found.value : [];
}

function adaptLegacyObserverAnalysis(source, availability) {
  const canonical = firstPresent(source, ['observer_analysis', 'observerAnalysis']);
  if (canonical.present) {
    availability.observerAnalysis = availabilityFor(true, canonical.value);
    return canonical.value;
  }

  // Compatibility belongs at this one decoding boundary. Older snapshots put
  // observer-derived visual classifications inside cognition. Promote only the
  // known legacy fields and mark their provenance; renderers never need to
  // guess whether a cognitive field was organism-owned or observer-derived.
  const cognition = source?.cognition;
  if (!cognition || typeof cognition !== 'object' || Array.isArray(cognition)) {
    availability.observerAnalysis = 'not_observed';
    return null;
  }
  const legacy = {};
  const derivation = {};
  for (const [key, description] of [
    ['activationClasses', 'legacy observer activation quantization'],
    ['predictionErrors', 'legacy observer prediction-error classification'],
    ['activationValues', 'legacy observer-preserved activation values'],
    ['predictionErrorValues', 'legacy observer-preserved prediction-error values'],
  ]) {
    if (Object.hasOwn(cognition, key) && cognition[key] != null) {
      legacy[key] = cognition[key];
      derivation[key] = `${description}; adapted at snapshot boundary`;
    }
  }
  if (!Object.keys(legacy).length) {
    availability.observerAnalysis = 'not_observed';
    return null;
  }
  availability.observerAnalysis = 'observed';
  return {
    ...legacy,
    derivation,
    provenance: {
      owner: 'observer',
      source: 'legacy-cognition-adapter',
      feedsBack: false,
    },
  };
}

function organismCognitionOnly(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return value;
  const cleaned = { ...value };
  for (const key of LEGACY_OBSERVER_FIELDS) delete cleaned[key];
  return cleaned;
}

/**
 * Apply one rich Mind snapshot to the shared passive view state.
 * Returns false only when the payload carries no usable snapshot.
 *
 * ``snap.availability`` preserves the distinction between a field that was not
 * observed, an explicitly-null field and an observed empty collection. Views
 * may keep array-shaped presentation state without turning absence into fact.
 */
export function applyMindSnapshot(raw) {
  const source = raw?.snapshot ?? raw;
  if (!source) return false;

  const availability = {};
  snap.tick = scalar(source, availability, 'tick', 'tick');
  snap.senses = collection(source, availability, 'senses', 'senses', 'percepts');
  snap.beliefs = collection(source, availability, 'beliefs', 'beliefs');
  const rawCognition = scalar(source, availability, 'cognition', 'cognition');
  snap.observerAnalysis = adaptLegacyObserverAnalysis(source, availability);
  snap.cognition = organismCognitionOnly(rawCognition);
  snap.topology = scalar(source, availability, 'topology', 'topology');
  snap.atlas = scalar(source, availability, 'atlas', 'atlas');
  snap.selfModel = scalar(source, availability, 'selfModel', 'self_model', 'selfModel');
  snap.bodySchema = scalar(source, availability, 'bodySchema', 'body_schema', 'bodySchema');
  snap.sensoryPhenotype = scalar(
    source,
    availability,
    'sensoryPhenotype',
    'sensory_phenotype',
    'sensoryPhenotype',
  );
  snap.sensoryDevelopment = collection(
    source,
    availability,
    'sensoryDevelopment',
    'sensory_development',
    'sensoryDevelopment',
  );
  snap.sensoryRelations = collection(
    source,
    availability,
    'sensoryRelations',
    'sensory_relations',
    'sensoryRelations',
  );
  snap.metabolism = scalar(source, availability, 'metabolism', 'metabolism');
  snap.degradation = scalar(source, availability, 'degradation', 'degradation');
  snap.development = scalar(source, availability, 'development', 'development');
  snap.sampling = scalar(source, availability, 'sampling', 'sampling');
  snap.details = scalar(source, availability, 'details', 'details');
  snap.displayId = scalar(source, availability, 'displayId', 'display_id', 'displayId');
  snap.instanceId = scalar(source, availability, 'instanceId', 'instance_id', 'instanceId');
  snap.organismState = scalar(
    source,
    availability,
    'organismState',
    'organism_state',
    'organismState',
  );
  snap.observerSemantics = scalar(
    source,
    availability,
    'observerSemantics',
    'observer_semantics',
    'observerSemantics',
  );
  snap.provenance = scalar(source, availability, 'provenance', 'provenance');
  snap.sensorimotor = scalar(source, availability, 'sensorimotor', 'sensorimotor');
  snap.embodiment = scalar(source, availability, 'embodiment', 'embodiment');
  snap.outcome = scalar(source, availability, 'outcome', 'outcome');
  snap.agencyAcquisition = scalar(
    source,
    availability,
    'agencyAcquisition',
    'agency_acquisition',
    'agencyAcquisition',
  );
  snap.affordances = collection(source, availability, 'affordances', 'affordances');
  snap.executiveIntention = scalar(
    source,
    availability,
    'executiveIntention',
    'executive_intention',
    'executiveIntention',
  );
  snap.availability = availability;
  return true;
}
