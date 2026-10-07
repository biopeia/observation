---
id: design.core.mathematical-foundations-and-temporal-scales-v1
title: "Mathematical Foundations and Temporal Scales v1"
document_type: design
domain: core
status: proposed
canonical: false
implementation_status: not_started
date: 2026-10-07
depends_on:
  - docs/governance/constitution.md
  - docs/adr/ADR-0015-immutable-mathematical-kernel-and-data-plasticity.md
  - docs/adr/ADR-0030-bayesian-evidence-saturation-and-anti-fossilization-cap.md
  - symbiont/docs/explanation/math/README.md
language: es
---

# Mathematical Foundations and Temporal Scales v1

**Estado:** **Proposed** (propuesta de diseño transversal; no autoriza implementación inmediata ni altera el comportamiento del organismo en este commit).  
**Fecha:** 2026-10-07.  
**Dominio:** Core / Foundations / Embodiment / Cognition.  
**Dependencias canónicas:**
- [docs/governance/constitution.md](../../governance/constitution.md) (Invariantes arquitectónicos, epistemológicos y de límites de dominio).
- [docs/adr/ADR-0015-immutable-mathematical-kernel-and-data-plasticity.md](../../adr/ADR-0015-immutable-mathematical-kernel-and-data-plasticity.md) (Núcleo matemático cerrado y plasticidad numérica).
- [docs/adr/ADR-0030-bayesian-evidence-saturation-and-anti-fossilization-cap.md](../../adr/ADR-0030-bayesian-evidence-saturation-and-anti-fossilization-cap.md) (Saturación de evidencia y techo antifosilización).
- [symbiont/docs/explanation/math/README.md](../../../symbiont/docs/explanation/math/README.md) (Compendio matemático canónico P1.5 / commit `82a2850d0a29`).

---

## 1. Resumen ejecutivo y principios de diseño

Este documento formaliza una revisión exhaustiva del fundamento matemático de Symbiont. Establece principios rigurosos para eliminar acoplamientos accidentales con el planificador (*scheduler*), erradicar constantes heurísticas no interpretables, resolver duplicidades teóricas en los modelos de memoria y deslindar estrictamente las escalas temporales e inferenciales del organismo.

El principio rector del sistema es:

> **Ninguna constante o fórmula entra en Symbiont por su elegancia. Cada operación matemática debe corresponder a un fenómeno físico identificable, una inferencia necesaria o una representación epistemológicamente respaldada.**

### 1.1 Decisiones ontológicas sobre constantes y primitivas

1. **Exclusión radical de $\varphi$ (número áureo):** No existe justificación científica ni empírica para su presencia en morfología, cognición, ontogenia ni plasticidad. Queda terminantemente proscrito del runtime.
2. **Confinamiento físico de $\pi$:** Permanece exclusivamente donde emerja de leyes geométricas, rotaciones articulares, fase de osciladores o dinámica física corporal. No pertenece al núcleo cognitivo abstracto.
3. **Validez natural de $e$ y $\ln$:** Permanecen como bases naturales para procesos de relajación continua, disipación, decaimiento exponencial, verosimilitud y teoría de la información.
4. **Exclusión en runtime de teoría de la información y objetivos globales:**
   - La entropía de Shannon $H(X)$, la información mutua $I(X; Y)$ y la entropía de transferencia $TE_{X \to Y}$ **no entran en el organismo runtime**. Se clasifican estrictamente como *instrumentos de observación científica externa en Lab* pendientes de estudios de validación independientes.
   - La información mutua es simétrica y no discrimina causante de consecuencia, por lo que no sustituye la atribución causal sensorimotora.
   - El *empowerment* ($\max I(A; S')$) y el *Bayesian Brain* global quedan expresamente rechazados como objetivos o arquitecturas monolíticas del organismo, respetando la Constitución §3 (prohibición de funciones de recompensa o utilidad globalmente impuestas).
5. **Conservación provisional bajo falsación:** Se preservan provisionalmente aquellos mecanismos respaldados por la evidencia y el compendio canónico:
   - Pérdida de Huber ($L_\delta(e)$) para errores de predicción acotados y diferenciables.
   - Línea base de persistencia (*persistence baseline*) como contrastador nulo no trivial.
   - Modelos predictivos hacia adelante (*forward prediction*).
   - Algoritmos online de momentos (Welford para medias y covarianzas recursivas).
   - Filtrado EWMA y factores de olvido exponencial con escalas explícitas.
   - Competencia motora derivada estrictamente de evidencia empírica acumulada.
   - Ponderación exponencial de responsabilidad en mezclas temporales.

---

## 2. Reconciliación con el compendio matemático y gobernanza

La clasificación matemática canónica (`symbiont/docs/explanation/math/01..10`, consolidada en el commit `82a2850d0a2955f0de2822423ca5241029980d9c`) categorizó las piezas del sistema como `[FORMAL]`, `[CODE]`, `[HISTORICAL]` o `[STUDY]`. Este diseño reconcilia dicha clasificación con la realidad del código en `symbiont/src/symbiont`:

1. **ADR-0015 (Núcleo matemático inmutable):** Garantiza que toda adaptación sea plasticidad paramétrica acotada (`KernelLimits`), sin generación de código dinámico. La formalización de constantes temporales e incertidumbre no amplía la capacidad del kernel, sino que formaliza el significado de sus estados continuos.
2. **ADR-0030 (Saturación de evidencia):** Introdujo un techo superior $E_{\max} = 32.0$ para prevenir la fosilización cognitiva en modelos bayesianos conjugados. Aunque el compendio clasifica el modelo `BeliefModel` original como residuo histórico sustituido en runtime por `EvidenceRevisionLedger` y `DissentRecord`, el principio de horizonte efectivo finito sigue siendo vinculante.
3. **`foundation/epistemic.py` (`EpistemicConventions`):** Define actualmente `RecencyClass` con umbrales discretos `(10, 40, 120, 400)` ticks y ticks representativos `(0, 10, 40, 120, 400)`. Esta cuantización categórica actúa como una discretización con pérdida que actualmente contamina el estado interno cuando se deserializa de forma inversa.

---

## 3. Deslinde formal de las escalas temporales ($T_p, T_s, T_e, T_d$)

### 3.1 El problema de la polisemia del `tick`

Actualmente, el término `tick` asume simultáneamente cuatro funciones dispares:
- **Tiempo físico determinista ($T_p$):** La evolución del integrador somático (temperatura, viscoelasticidad muscular, fatiga).
- **Índice secuencial de ciclo ($T_s$):** El ciclo discreto de llamada del bucle vital del organismo (`symbiont_tick`).
- **Experiencia u observaciones efectivas ($T_e$):** El conteo o masa de eventos independientes realmente percibidos ($N_{\text{eff}}$).
- **Desarrollo longitudinal ($T_d$):** Épocas de consolidación estructural, ontogenia y estabilidad a través de sesiones de reencarnación.
- **Tiempo de infraestructura:** Tiempos de pared del host (`time.monotonic_ns()`), despacho de mensajes o renderizado de observabilidad.

Invariante fundamental:
$$\boxed{T_s \not\equiv T_p \not\equiv T_e \not\equiv T_d}$$

Un tick de Symbiont es un cuanto determinista. El defecto fundamental en la física del organismo **no reside en el reloj de pared del host ni en los FPS de ejecución**, sino en que la configuración determinista `physics_substeps_per_tick` puede variar entre experimentos o entornos (por ejemplo, 1, 2, 5 o 10 subpasos de integración del solucionador de física por cada tick cognitivo). En el código actual, mientras el solucionador físico avanza $N \cdot \delta t$, las dinámicas fisiológicas internas (`HomeostaticController.constitutive_step()`) avanzan en cantidades fijas por tick, haciendo que la fisiología mute según cuántos subpasos se configuren en la simulación.

### 3.2 Análisis constitucional: Frontera de Embodiment y paso de $\Delta t$

De acuerdo con la [Constitución de Symbiont Lab](../../governance/constitution.md):
- **§1 Ontological boundaries & §9 Embodiment:** Symbiont es el sujeto cognoscente; el Cuerpo (*Body*) es la entidad física; Embodiment es el acoplamiento entre ambos.
- **§2 Own state versus external knowledge:** Symbiont no debe recibir verdades del simulador, etiquetas evaluadoras ni marcas de tiempo del host.
- **§14 Determinism and seeds:** La evolución debe depender exclusivamente de semillas y configuración determinista.

**Resolución arquitectónica:**
1. ¿Puede el organismo recibir un `Δt` físico?  
   **No en su núcleo cognitivo.** La cognición es un proceso informacional puro que opera sobre canales sensoriales opacos y relaciones secuenciales; no debe "saber" qué es un segundo ni recibir un reloj físico.
2. ¿Dónde pertenece el $\Delta t$ físico?  
   Pertenece exclusivamente al **controlador somático fisiológico** (`core/embodiment/homeostasis.py` y `physiology.py`).
3. Origen legítimo de $\Delta t$:  
   Cualquier $\Delta t$ suministrado al sustrato somático debe derivarse estrictamente de parámetros deterministas de la simulación:
   $$\Delta t = \text{physics\_substeps\_per\_tick} \times \delta t_{\text{physics}}$$
   **Nunca** debe provenir de `time.monotonic()` ni del reloj del sistema operativo.
4. Percepción cognitiva de la fisiología:  
   La cognición percibe únicamente señales interoceptivas opacas (desviación homeostática, fatiga, hambre metabólica) resultantes de la integración, manteniendo la invariancia epistemológica sin fugas de magnitudes absolutas externas.

---

## 4. Semántica unificada de decaimiento y memoria

### 4.1 Núcleo canónico de decaimiento

Cualquier proceso de atenuación temporal debe responder a la familia exponencial canónica:
$$D(\Delta; h) = 2^{-\Delta / h} = \exp\left(-\frac{\ln 2}{h} \Delta\right)$$
donde $h > 0$ es la **vida media** expresada en la escala correspondiente:
- Segundos físicos ($T_p$) para procesos somáticos (e.g., relajación térmica).
- Observaciones o interacciones ($T_e$) para modelos predictivos y crédito asociativo.
- Ciclos vitales o épocas ($T_d$) para consolidación estructural o poda de hipótesis inactivas.

### 4.2 Resolución formal de la duplicidad en `predictive_credit`

En `sensory/predictive_credit.py` confluyen actualmente dos valores derivados del factor de olvido $\lambda = 0.97$:
1. **Vida media ($h$):**
   $$h = \frac{\ln(0.5)}{\ln(0.97)} \approx 22.756 \approx 22.8 \text{ observaciones}$$
   Representa el número de observaciones tras el cual el peso de una muestra individual cae al 50%.
2. **Masa muestral efectiva asintótica ($N_{\infty}$ o memoria horizonte):**
   $$N_{\infty} = \sum_{k=0}^{\infty} \lambda^k = \frac{1}{1 - \lambda} = \frac{1}{1 - 0.97} \approx 33.333 \approx 33.3 \text{ observaciones}$$
   Representa el límite superior de la suma de pesos acumulados en los estadísticos suficientes recursivos ($\sum x, \sum y, \sum x^2, \sum xy$).

**Dictamen:** Ambas magnitudes son matemáticamente rigurosas pero describen propiedades completamente distintas: una es una escala de *atenuación individual* y la otra es una escala de *acumulación muestral agregada*. El diseño formal exige:
- Prohibir la sustitución arbitraria de una por otra.
- Nombrar explícitamente `evidence_half_life = 22.8` y `asymptotic_effective_horizon = 33.3`.
- Resolver la inconsistencia interna de `PairwisePredictiveEvidence`: actualmente coexiste $\lambda = 0.97$ para los estadísticos de regresión con un filtro EWMA de ganancia con $\alpha = 0.15$ ($\lambda = 0.85$, cuya vida media es $h \approx 4.3$ y su masa asintótica $N_{\infty} \approx 6.7$). La ganancia se olvida 5 veces más rápido que los datos que la fundamentan sin declaración explícita.

---

## 5. Auditoría de madurez epistemológica frente a edad cronológica

Un error epistemológico recurrente en el código actual es el uso de `age_ticks` como sucedáneo de solidez o madurez de representaciones y componentes:
- En `sensory/sensor.py`: un sensor pasa a `ESTABLISHED` a los 16 ticks y a `SPECIALISED` a los 64 ticks, incluso si no ha recibido lecturas informativas o si sus entradas son nulas o estáticas.
- En `sensory/system.py`: `sensor.age_ticks += 1` avanza mecánicamente en cada ciclo en que hay lectura disponible, sin evaluar entropía, varianza ni poder predictivo.
- En `cognition/structure.py`: las conexiones sinápticas tentativas se eliminan si `edge.age_ticks >= tentative_lifetime_ticks`, mientras que el soporte real sólo cuenta coactivaciones brutas y `del tick` desecha la dimensión temporal.

**Invariante de madurez:**
$$\boxed{\text{Edad cronológica } (T_s) \neq \text{Madurez epistemológica } (\mathcal{M})}$$
La madurez de un sensor, nodo o competencia debe depender de:
1. Tamaño muestral efectivo ($N_{\text{eff}}$).
2. Variabilidad observable no colapsada ($\sigma^2 > \epsilon_{\text{floor}}$).
3. Estabilidad en la reducción del error predictivo respecto a la persistencia.
4. Consistencia direccional y baja incertidumbre relativa ($\hat{\mu} / (\hat{\sigma}/\sqrt{N_{\text{eff}}})$).

---

## 6. Auditoría de proyecciones discretas de frescura (*Recency*)

En `foundation/epistemic.py`, `RecencyClass` se define como:
- `CURRENT` ($< 10$ ticks inactivos)
- `SHORT_IDLE` ($< 40$ ticks inactivos)
- `IDLE` ($< 120$ ticks inactivos)
- `LONG_IDLE` ($< 400$ ticks inactivos)
- `DORMANT` ($\ge 400$ ticks inactivos)

Y se asignan "ticks representativos": `(0, 10, 40, 120, 400)`.

### 6.1 Fabricación de historia temporal sintética

La distorsión más grave ocurre en la reconstrucción o deserialización de estado:
- En `core/cognition/host_self_model.py` (L213–216):
  ```python
  representative_idle = _RECENCY_REPRESENTATIVE_IDLE_TICKS[RecencyClass(recency_class_raw)]
  last_observed_tick = max(0, current_tick - representative_idle)
  ```
- En `core/embodiment/body_schema.py` (L486–494 y L1264–1271):
  ```python
  representative_idle = _RECENCY_REPRESENTATIVE_IDLE_TICKS[RecencyClass(recency_raw)]
  last_evidence_tick = max(0, current_tick - representative_idle)
  ```

**Pérdida de información demostrada:**
1. Al proyectar un valor continuo de inactividad (e.g. 39 ticks) a `SHORT_IDLE`, y luego restaurarlo a 10 ticks, se destruyen 29 ticks de historia real.
2. Si un sensor estaba inactivo hace 399 ticks (`LONG_IDLE`), al restaurar se fija sintéticamente en 120 ticks, falseando su frescura en 279 ticks.
3. Se fabrica un `last_observed_tick` apócrifo que jamás existió en la experiencia del organismo.

**Diseño objetivo:**
Las categorías `CURRENT`, `IDLE`, etc., deben ser **proyecciones de lectura exclusivamente para visualización, gobernanza o telemetría pasiva**. La fuente de verdad interna debe preservar el instante determinista exacto o la frescura continua:
$$F(\Delta) = 2^{-\Delta / h_{\text{recency}}}$$

---

## 7. Matriz canónica de fórmulas y mecanismos actuales

La siguiente matriz constituye el núcleo técnico de la propuesta. Clasifica cada fórmula actual, su defecto demostrado, su reloj implícito, su forma matemática objetivo y la prueba de equivalencia o falsación requerida antes de cualquier migración de código.

| Mecanismo / Fórmula actual | Archivo / Líneas | Escala o reloj implícito | Significado actual | Defecto demostrado | Forma objetivo | Compatibilidad arquitectónica | Prueba de equivalencia / falsación |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Relajación térmica:**<br>$T_{n+1} = T_n + (T^* - T_n) \cdot r$<br>donde $r = 0.02$ | [`core/embodiment/homeostasis.py:134-137`](../../../symbiont/src/symbiont/core/embodiment/homeostasis.py#L134-L137)<br>[`physiology_config.py:32`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L32) | Discreto por llamada ($T_s$) | Disipación térmica hacia setpoint por tick. | Si `physics_substeps_per_tick` cambia, el tiempo físico por tick cambia, pero la relajación avanza igual por tick, desincronizando la física de la termodinámica. | Dinámica continua en tiempo físico determinista:<br>$T(t + \Delta t) = T^* + (T(t) - T^*) e^{-\Delta t / \tau_{\text{thermal}}}$<br>con $\Delta t = k_{\text{substeps}} \cdot \delta t_{\text{physics}}$. | Confinado al controlador somático de Embodiment. Cognición recibe sólo desviación interoceptiva. | **Test G1:** Dos simulaciones con la misma semilla y mismo tiempo físico total (e.g., $1.0\text{ s}$), una con $k=2$ y otra con $k=10$, deben converger a $T$ final idéntica dentro de tolerancia numérica. |
| **Recuperación de fatiga:**<br>$\Delta \text{fatiga} = -r_{\text{recov}} \cdot (2 \text{ if resting else } 1)$<br>con $r_{\text{recov}} = 0.02$ | [`core/embodiment/homeostasis.py:127-131`](../../../symbiont/src/symbiont/core/embodiment/homeostasis.py#L127-L131)<br>[`physiology_config.py:28`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L28) | Discreto por llamada ($T_s$) | Recuperación fija de fatiga acumulada en cada tick. | Acoplado al número de ticks y no a la duración física del descanso. | Desintegración exponencial o tasa continua:<br>$\text{Fatiga}(t+\Delta t) = \text{Fatiga}(t) e^{-\Delta t / \tau_{\text{fatigue}}} + \text{Trabajo} \cdot g_w$. | Local a la fisiología somática. No expone constantes temporales a la cognición. | **Test G1:** Variar `physics_substeps_per_tick` mantiene idéntica la curva de recuperación de fatiga para igual trabajo físico real. |
| **Reparación tisular autónoma:**<br>$\text{repair} = \min(1-I, r_{\text{repair}}, E_{\text{disp}})$<br>con $r_{\text{repair}} = 0.02$ | [`core/embodiment/homeostasis.py:147-156`](../../../symbiont/src/symbiont/core/embodiment/homeostasis.py#L147-L156)<br>[`physiology_config.py:26`](../../../symbiont/src/symbiont/core/embodiment/physiology_config.py#L26) | Discreto por llamada ($T_s$) | Incremento lineal de integridad por tick acotado por energía. | Dependencia del ritmo de llamadas del bucle vital para regenerar daño estructural. | Integración continua acotada por flujo de potencia energética:<br>$\frac{dI}{dt} = \min\left(\frac{1-I}{\tau_{\text{repair}}}, \dot{E}_{\text{maint}}, r_{\max}\right)$. | Control metabólico somático inalterado en interfaz; cargo continuo al `MetabolicLedger`. | **Test G1:** Misma tasa de regeneración por segundo físico determinista bajo diferente resolución de integración. |
| **Reproducibilidad motora:**<br>$R = \frac{1}{1 + 25 \sigma^2}$ | [`actuation/sensorimotor.py:220,1174,1382`](../../../symbiont/src/symbiont/actuation/sensorimotor.py#L220)<br>[`actuation/competence.py:56`](../../../symbiont/src/symbiont/actuation/competence.py#L56) | Experiencial ($T_e$) | Ponderación no lineal de varianza de efecto motor. | El factor `25.0` es una constante heurística sin calibración. Equivale exactamente a exigir $\sigma^2 \le 0.02$ para $R \ge 2/3$. | Escalar de incertidumbre estandarizado:<br>$R = \frac{1}{1 + (\sigma / \sigma_0)^2}$<br>donde $\sigma_0$ es el umbral de varianza residual admisible fundamentado en el ruido de fondo sensor. | Invariante de competencia motora; no altera el pipeline de arbitraje. | **Test G4/G5:** Estudio adversarial de correlación entre $R$ derivado y predictibilidad real frente a perturbaciones motoras. |
| **Controlabilidad motora:**<br>$C = \max(0, \mu) \cdot R \cdot D$<br>con umbral $C > 0.002$ | [`actuation/sensorimotor.py:1176,1383,1395`](../../../symbiont/src/symbiont/actuation/sensorimotor.py#L1176)<br>[`actuation/competence.py:55`](../../../symbiont/src/symbiont/actuation/competence.py#L55) | Experiencial ($T_e$) | Producto de magnitud de efecto medio, reproducibilidad y consistencia direccional. | Mezcla magnitud bruta $\mu$ con normalizaciones sin dimensión; el umbral $0.002$ define la ontología motora arbitrariamente. | Relación señal-ruido estandarizada de agencia:<br>$Z_{\text{agency}} = \frac{|\hat{\mu}|}{\hat{\sigma} / \sqrt{N_{\text{eff}}} + \epsilon} \cdot D$<br>comparado con efecto inducido pasivo. | Respeta ADR-0022 (representación factorizada de efectos) y ADR-0014. | **Test G5:** Calibración de falsos positivos en atribución de agencia bajo exploraciones pasivas nulas. |
| **Madurez de sensores:**<br>Umbrales rígidos:<br>$\text{age} \ge 4 \to \text{IMMATURE}$<br>$\text{age} \ge 16 \to \text{ESTABLISHED}$<br>$\text{age} \ge 64 \to \text{SPECIALISED}$ | [`sensory/sensor.py:142-153`](../../../symbiont/src/symbiont/sensory/sensor.py#L142-L153)<br>[`sensory/system.py:295-298`](../../../symbiont/src/symbiont/sensory/system.py#L295-L298) | Ciclos del sistema ($T_s$) | Transición de estado de madurez según ticks transcurridos desde creación. | Sensores sin variación o en régimen de fallo adquieren madurez si sobreviven 64 ticks; la edad sustituye la evidencia. | Madurez basada en soporte informacional efectivo:<br>$\mathcal{M} = f(N_{\text{eff}}, \sigma_{\text{signal}}^2, \text{Gain}_{\text{pred}})$.<br>Exigir $N_{\text{eff}} \ge N_{\min}$ y persistencia explicada. | Mantiene los estados de `MaturityState`, pero su transición la gobierna la evidencia empírica. | **Test G4:** Un sensor alimentado con ruido constante no debe madurar más allá de `NASCENT` independientemente de los ticks. |
| **Factor de madurez en confianza:**<br>$\text{conf} = 0.7 H + 0.3 \min(1, \frac{\text{age}}{16})$ | [`sensory/sensor.py:157-158`](../../../symbiont/src/symbiont/sensory/sensor.py#L157-L158) | Ciclos del sistema ($T_s$) | Mezcla lineal de salud ($H$) y fracción de edad en 16 ticks. | Ponderación fija arbitraria ($0.7 / 0.3$) que asume que a los 16 ticks cualquier sensor es maduro. | Confianza ponderada por estabilidad de señal:<br>$\text{conf} = H \cdot \left(1 - \frac{1}{\sqrt{N_{\text{eff}} + 1}}\right)$. | Mantiene rango $[0, 1]$ de confianza sin contaminar el cálculo con ticks brutos. | **Test G5:** Intervalo de confianza calibrado frente a varianza observada de la señal. |
| **Duplicidad en crédito predictivo:**<br>$\lambda = 0.97 \to h \approx 22.8$<br>asintótico: $N_{\infty} \approx 33.3$<br>EWMA error: $\alpha = 0.15 \to h \approx 4.3$ | [`sensory/predictive_credit.py:10-11,61,69,116`](../../../symbiont/src/symbiont/sensory/predictive_credit.py#L10-L11) | Experiencial ($T_e$) | Olvido exponencial en regresión lag-1 acoplado con EWMA de ganancia. | Dos escalas de memoria incompatibles ($h \approx 22.8$ vs $h \approx 4.3$) sin explicitar su desfase dinámico. | Declaración unificada de vida media experiencial:<br>$h_{\text{evidence}} = 24 \text{ obs}$, $h_{\text{gain}} = 24 \text{ obs}$,<br>derivando $\lambda = 2^{-1/h}$ y $N_{\infty} = \frac{1}{1 - \lambda}$. | Preserva la formulación lag-1 y comparación contra persistencia sin alterar interfaz de créditos. | **Test G2:** Mismo historial de observaciones produce idéntica ordenación de candidatos predictivos. |
| **Frescura social:**<br>$F = e^{-\ln(2) \cdot \frac{\Delta \text{ticks}}{32}}$ | [`core/social/relations.py:46,81`](../../../symbiont/src/symbiont/core/social/relations.py#L46)<br>[`modeling/culture.py:1282`](../../../symbiont/src/symbiont/modeling/culture.py#L1282) | Ciclos vitales ($T_s$) | Decaimiento de evidencia social con vida media de 32 ticks. | Si el organismo está inactivo socialmente pero computando intensamente, la relación decae aunque no hayan ocurrido eventos sociales. | Vida media en escala experiencial o de interacción:<br>$F = 2^{-\Delta_{\text{interactions}} / h_{\text{social}}}$<br>o $T_p$ si la memoria es temporal. | Conforme con ADR-0041 y el modelo de evidencia social descentralizada. | **Test G2:** Replay de interacciones sociales produce idéntica degradación sin importar el intervalo entre llamadas. |
| **Reconstrucción sintética de ticks en recency:**<br>`last_tick = max(0, now - repr_idle)` | [`core/cognition/host_self_model.py:213-216`](../../../symbiont/src/symbiont/core/cognition/host_self_model.py#L213-L216)<br>[`core/embodiment/body_schema.py:486,1264`](../../../symbiont/src/symbiont/core/embodiment/body_schema.py#L486) | Ciclos vitales ($T_s$) | Asignación de ticks sintéticos a partir de bins categóricos (`RecencyClass`). | Destruye la continuidad real y genera saltos temporales arbitrarios al guardar y restaurar checkpoints. | Persistir la frescura continua $F \in [0, 1]$ o el identificador exacto del último ciclo de evidencia; usar categorías solo como proyecciones de vista. | Mantiene compatibilidad con esquemas de persistencia y serialización sin inventar historia. | **Test G2:** Invarianza de checkpoint/restore: serializar y deserializar no altera la frescura calculada del componente. |
| **Poda sináptica por edad tentativa:**<br>`edge.age_ticks >= tentative_lifetime_ticks` | [`cognition/structure.py:474-476,488-494`](../../../symbiont/src/symbiont/cognition/structure.py#L474-L476) | Ciclos del sistema ($T_s$) | Eliminación de conexiones tentativas si no alcanzan soporte en $K$ ticks. | La poda depende del número de ticks cognitivos transcurridos y no del número de oportunidades de activación conjunta. | Poda condicionada a intentos u oportunidades efectivas:<br>`trials >= min_trials and support / trials < threshold`. | Estrictamente respetuoso con `KernelLimits` (ADR-0015) y Oja update (ADR-0031). | **Test G6:** Ablación de poda por edad vs poda por oportunidades: reducción de poda errónea en regímenes de baja actividad. |
| **Ponderación exponencial de responsabilidad:**<br>$w_i = \exp(-\Delta L_i / T)$<br>con $T = 0.25$ fijo | [`modeling/responsibility.py`](../../../symbiont/src/symbiont/modeling/responsibility.py)<br>[`cognition/learning.py`](../../../symbiont/src/symbiont/cognition/learning.py) | Sin dimensión empírica | Softmax sobre diferencias absolutas de pérdida de Huber. | La temperatura $T=0.25$ no está normalizada frente a la escala de la señal; si la escala de pérdida varía, el reparto colapsa o se aplana. | Diferencia estandarizada:<br>$z_i = \frac{L_i - L_{\min}}{\hat{\sigma}_L + \epsilon}$, $w_i = \exp(-z_i / T_{\text{rel}})$. | Mantiene la formulación de mezcla de expertos pero inmune a la escala de amplitud del sensor. | **Test G5:** Calibración de pesos relativos ante señales escaladas por factores de $0.1\times$ y $10\times$. |
| **Marca de tiempo fallback del host:**<br>`tick_timestamp_ns = max(..., default=time.monotonic_ns())` | [`core/domains/perception.py:100-103`](../../../symbiont/src/symbiont/core/domains/perception.py#L100-L103) | Tiempo de pared del host (infraestructura) | Asignación de timestamp de lectura cuando el host no suministra lecturas. | Introduce reloj no determinista en el núcleo del percepto, violando la reproducibilidad estricta. | Reemplazar por tiempo causal determinista del paso:<br>$t_{\text{causal}} = t_{\text{origin}} + k_{\text{tick}} \cdot \Delta t_{\text{cycle}}$. | Respeta ADR-0042 (tiempo causal determinista) y la Constitución §14. | **Test G2:** Determinismo byte-a-byte idéntico en ejecuciones con pausas de host inducidas. |

---

## 8. Marco de validación científica y puertas de equivalencia

Cualquier futura migración de código derivada de este diseño no se evaluará por su elegancia formal, sino por el estricto cumplimiento de las siguientes **puertas científicas (Gates G1–G8)**:

### G1 — Invarianza frente a resolución física (*Physics Substep Invariance*)
- **Protocolo:** Ejecutar el mismo organismo en el mismo entorno con semilla fijada durante un tiempo físico total idéntico (e.g. $t_{\text{físico}} = 10.0\text{ s}$).
- **Brazo A:** `physics_substeps_per_tick = 1` ($\delta t_{\text{tick}} = 0.02\text{ s}$, 500 ticks cognitivos).
- **Brazo B:** `physics_substeps_per_tick = 5` ($\delta t_{\text{tick}} = 0.10\text{ s}$, 100 ticks cognitivos).
- **Criterio de éxito:** Las variables fisiológicas somáticas finales (temperatura corporal, fatiga recuperada, tejido reparado) deben ser numéricamente equivalentes dentro de la tolerancia de discretización del integrador ($\epsilon \le 10^{-3}$).

### G2 — Equivalencia de repetición determinista (*Replay Equivalence*)
- El historial de entradas idéntico debe producir exactamente la misma trayectoria de inferencia y pesos, sin variaciones originadas por marcas de tiempo del sistema operativo o pausas del planificador.

### G3 — Invarianza ante no inyección semántica (*No Semantic Injection*)
- Ninguna constante o fórmula modificada puede incorporar etiquetas del mundo exterior, nombres biológicos artificiales ni funciones de aptitud/éxito ocultas (Constitución §2 y §3).

### G4 — Superación de línea base predictiva (*Predictive Improvement*)
- Cualquier nuevo estimador de madurez o selección de sensores debe demostrar empíricamente una ganancia predictiva estrictamente superior a la línea base de persistencia trivial en los registros de evaluación.

### G5 — Calibración de incertidumbre (*Uncertainty Calibration*)
- A medida que el número de observaciones independientes $N_{\text{eff}}$ crece, la incertidumbre calculada $\hat{\sigma}/\sqrt{N_{\text{eff}}}$ debe decrecer monotónicamente, sin sufrir fosilización ni colapsos numéricos (ADR-0030).

### G6 — Falsación y ablación (*Ablation Integrity*)
- La eliminación de las heurísticas mágicas (`25.0`, `0.002`, `16 ticks`) debe demostrar en estudios comparativos de Lab que no degrada la estabilidad de adquisición de competencias motoras ni la formación del esquema corporal.

### G7 — Neutralidad motivacional (*No Hidden Reward*)
- Ninguna medida informacional (entropía, ganancia o varianza) podrá utilizarse como señal de refuerzo, recompensa intrínseca ni función de pérdida conductual sin un diseño previo aprobado por gobernanza.

### G8 — Preservación del presupuesto computacional (*Computational Budget*)
- La formalización matemática debe operar estrictamente en tiempo acotado $O(1)$ o $O(\log N)$ por tick, respetando los límites de `KernelLimits` (ADR-0015).

---

## 9. Hoja de ruta de implementación desacoplada (M0–M7)

Para garantizar la no interferencia con el desarrollo en curso, la adopción de este diseño se estructurará en fases incrementales:

- **Fase M0 (Catálogo y auditoría de constantes):** Sin cambios de comportamiento en runtime. Registro completo de todas las constantes empíricas y su fuente en la literatura o heurística histórica.
- **Fase M1 (Tiempo tipado e interfaces de escala):** Introducción de primitivas de escala temporal sin alterar las ecuaciones cognitivas. Aislamiento formal del $\Delta t$ somático.
- **Fase M2 (Fisiología somática continua):** Migración de `HomeostaticController` a integradores continuos dependientes de $\Delta t$ físico determinista. Superación del **Gate G1**.
- **Fase M3 (Semántica unificada de decaimiento):** Estandarización de vida media en memorias experienciales y resolución de la duplicidad en `PairwisePredictiveEvidence`.
- **Fase M4 (Madurez basada en evidencia):** Desacoplamiento de `age_ticks` en `SensoryNode`, `SensorySystem` y `CognitiveGraph`. Sustitución por masa de soporte $N_{\text{eff}}$.
- **Fase M5 (Controlabilidad y agencia v2):** Estudio experimental en Lab de la relación señal-ruido $Z_{\text{agency}}$ frente a la fórmula heredada $C = \mu \cdot \frac{1}{1+25\sigma^2} \cdot D$.
- **Fase M6 (Diagnóstico informacional en Lab):** Implementación de estimadores de entropía $H$ y transferencia de información $TE$ **únicamente en `lab/`**, como herramientas de observación externa del investigador.
- **Fase M7 (Dictamen de promoción):** Evaluación científica de si algún estimador informacional de Lab amerita su promoción controlada hacia el núcleo del organismo bajo un ADR específico.
