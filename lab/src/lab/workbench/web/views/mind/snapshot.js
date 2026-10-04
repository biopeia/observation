import { snap } from './state.js';

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
  snap.cognition = scalar(source, availability, 'cognition', 'cognition');
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
  snap.observerAnalysis = scalar(
    source,
    availability,
    'observerAnalysis',
    'observer_analysis',
    'observerAnalysis',
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
