import { tel } from './state.js';

/**
 * Epistemic availability for complete telemetry projections.
 *
 * Values stay type-stable in `tel`; this parallel map preserves whether a
 * `null` was explicitly observed or whether the producer omitted the field.
 */
export const telemetryAvailability = Object.create(null);

function availabilityOf(data, source) {
  if (!Object.hasOwn(data, source)) return 'not_observed';
  const value = data[source];
  if (value === null) return 'observed_null';
  if (Array.isArray(value) && value.length === 0) return 'observed_empty';
  return 'observed';
}

function assignComplete(data, fields) {
  for (const [target, source] of fields) {
    // Each body/cognition/vitals event is a complete projection for that
    // channel at one tick. Missing therefore means "not observed now", not
    // "repeat the last observation". Preserve explicit false/0/null exactly.
    telemetryAvailability[target] = availabilityOf(data, source);
    tel[target] = Object.hasOwn(data, source) ? data[source] : null;
  }
}

export function resetTelemetryAvailability() {
  for (const key of Object.keys(telemetryAvailability)) {
    delete telemetryAvailability[key];
  }
}

const BODY_FIELDS = [
  ['tick', 'tick'],
  ['metabolicReserve', 'metabolic_reserve'],
];

const COGNITION_FIELDS = [
  ['tick', 'tick'],
  ['schemaConf', 'schema_confidence'],
  ['schemaParts', 'schema_parts'],
  ['schemaSensory', 'schema_sensory_parts'],
  ['schemaCognitive', 'schema_cognitive_regions'],
  ['embodimentEpoch', 'embodiment_epoch'],
  ['reacclimationRemaining', 'reacclimation_remaining'],
  ['reacclimating', 'reacclimating'],
  ['motorOrigin', 'motor_origin'],
  ['motorOriginDetail', 'motor_origin_detail'],
  ['predictorCount', 'predictor_count'],
  ['sensorimotorPatterns', 'sensorimotor_patterns'],
  ['motorPrimitives', 'motor_primitives'],
  ['cognitiveMotorPrimitives', 'cognitive_motor_primitives'],
  ['motorRepertoireSize', 'motor_repertoire_size'],
  ['recurrentPrimitiveCandidates', 'recurrent_primitive_candidates'],
  ['maxPrimitiveSamples', 'max_primitive_samples'],
  ['fullCompetenceGateCandidates', 'full_competence_gate_candidates'],
  ['motorReadoutNodes', 'motor_readout_nodes'],
  ['primitiveReadoutNodes', 'primitive_readout_nodes'],
  ['cognitiveMotorOutputEdges', 'cognitive_motor_output_edges'],
  ['cognitiveConcepts', 'cognitive_concepts'],
  ['cognitiveReadouts', 'cognitive_readouts'],
  ['predictionError', 'prediction_error'],
  ['prospective', 'prospective_selected'],
  ['prospectiveEV', 'prospective_expected_value'],
  ['slmActive', 'slm_active'],
  ['slmModels', 'slm_models'],
];

const VITAL_FIELDS = [
  ['tick', 'tick'],
  ['alive', 'alive'],
  ['jointMotion', 'joint_motion'],
  ['activeEffectors', 'active_effectors'],
  ['resourceDistance', 'resource_distance'],
  ['resourceProgress', 'resource_progress'],
  ['resourceRemaining', 'resource_remaining'],
  ['absorbedEnergy', 'absorbed_energy'],
  ['displacement', 'displacement_from_origin'],
  ['mechanicalWork', 'mechanical_work_joules'],
  ['positiveActuatorWork', 'positive_actuator_work_joules'],
  ['negativeActuatorWork', 'negative_actuator_work_joules'],
  ['absoluteActuatorWork', 'absolute_actuator_work_joules'],
  ['netActuatorWork', 'net_actuator_work_joules'],
  ['metabolicCost', 'metabolic_work_cost'],
];

/**
 * Apply one lightweight /api/organism event to shared telemetry state.
 * Returns true when a known telemetry type was consumed.
 */
export function applyTelemetryEvent(data) {
  if (!data?.type) return false;

  if (data.type === 'body') {
    assignComplete(data, BODY_FIELDS);
    return true;
  }

  if (data.type === 'cognition') {
    assignComplete(data, COGNITION_FIELDS);
    return true;
  }

  if (data.type === 'vitals') {
    assignComplete(data, VITAL_FIELDS);
    return true;
  }

  return false;
}
