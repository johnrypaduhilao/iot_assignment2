# Module 1 Assignment — Protocol Comparison Report

**Student Name:** ___________________________
**Student ID:**   ___________________________
**Date:**         ___________________________

---

## 5.1 QoS Comparison Results Table

> Run `pytest tests/mqtt/test_qos_loss.py -v -s` and paste the output table here.


| Protocol / QoS | Sent | Received | Lost (%) | Duplicates | Avg Latency (ms) |
|----------------|------|----------|----------|------------|-----------------|
| MQTT QoS 0 | 100 | 100| 0 | 0.0% | 0.7 |
| MQTT QoS 1 | 100 | 100 | 0 | 0.0% | 0.7 |
| MQTT QoS 2 | 100 | 100 | 0 | 0.0% | 1.3 |
| CoAP NON | | | | | |
| CoAP CON | | | | | |
| AMQP (confirms off) | | | | | |

**Analysis Questions:**

1. **Why does QoS 0 lose messages while QoS 1 and 2 do not?** *(2–3 sentences)*

   > _Your answer here_

2. **QoS 1 may show duplicates. Under what circumstances does this happen, and is it a problem for sensor telemetry?** *(2–3 sentences)*

   > _Your answer here_

3. **QoS 2 has higher latency than QoS 1. What causes this, and when is the trade-off worth it?** *(2–3 sentences)*

   > _Your answer here_

---

## 5.2 CoAP–HTTP Proxy Mapping

> Run `pytest tests/coap/test_proxy.py -v -s` and record the observed HTTP headers.

| HTTP Header | CoAP Option | Your Observed Value |
|-------------|-------------|---------------------|
| Content-Type | Content-Format (12) | application/json which is the innterpretation for CoAP Content Format(50) that server returns |
| Cache-Control: max-age | Max-Age (14) | Max-Age will be 60 since this is the default value if not overridden which our server did not. |
| ETag | ETag (4) | None. Server did not set any ETags |
| Location | Location-Path (8) | None. This only appears if we use resources that uses POST specifically 2.01 Created. Because we used GET automatically there is None. |

---

## 5.3 Protocol Selection Recommendation

*(500–700 words. Justify each recommendation with specific technical evidence from your implementation and packet captures.)*

### Data Path Recommendations

| Data Path | Recommended Protocol | Justification |
|-----------|---------------------|---------------|
| Sensor → Cloud (high frequency, <100 ms latency) | | |
| Actuator commands (safety-critical, exactly-once) | | |
| Backend service-to-service routing | | |
| OTA firmware delivery to constrained MCU (Class 2) | | |

### Detailed Justification

> *(Write 500–700 words here. Each recommendation must cite specific evidence — e.g. measured latency values from Section 5.1, packet overhead observed in Task 4, or implementation complexity experienced in Tasks 1–3.)*

---

## 5.4 Reflection

*(300–400 words addressing all three prompts below.)*

### Technical Challenge

> *Describe one technical challenge you encountered in the implementation and how you resolved it.*

### Most Surprising Protocol Difference

> *Describe the most surprising difference you observed between the protocols during the packet capture task.*

### Most Complex Protocol to Implement

> *Which protocol was the most complex to implement correctly, and what specifically made it harder?*

---

*Module 1 Assignment — Real-Time Data Analytics for IoT*
