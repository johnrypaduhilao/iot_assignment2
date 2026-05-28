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
| CoAP NON | | | | | (CoAP test_qos_loss.py does not exist) |
| CoAP CON | | | | | (CoAP test_qos_loss.py does not exist) | 
| AMQP (confirms off) | | | | | (skipped) | 

**Analysis Questions:**

1. **Why does QoS 0 lose messages while QoS 1 and 2 do not?** *(2–3 sentences)*
   > Honestly on my actual results above, I could not see lost messages for QoS 0 but upon checking the result from tshark captures, QoS 0 didn't use any handshake which means there is no acknowledgement. So if this is applied in real-world, QoS  0 is deployed in a lossy network there would be no mechanism to detect or recover dropped messages resulting to lose messages.

2. **QoS 1 may show duplicates. Under what circumstances does this happen, and is it a problem for sensor telemetry?** *(2–3 sentences)*

   > QoS 1 uses publish & puback handshake where duplicates can happen when puback is lost. One more thing I can support is the DUP flag in the fixed-header byte (33) shown in section 4.2, which was 0 here because nothing was retransmitted but will happen in real-world IoT applications. For sensor telemetry purposes repeated reading is harmless because the next reading will just replace the current one.

3. **QoS 2 has higher latency than QoS 1. What causes this, and when is the trade-off worth it?** *(2–3 sentences)*

   > QoS2 has visible latency above of 1.3 (almost double with QoS 0 & 1) which is mainly because it is doing a four-message handshake: publish, pubrec, pubrel and pubcomp unlike QoS 0 and 1 which uses simpler deliveries. To elaborate further these extra steps makes it more resilient but also means more latency is visible. This trade-off is worth it especially in safety-critical systems that may cause an actual harm to the users.

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
| Sensor → Cloud (high frequency, <100 ms latency) | MQTT using QoS 0 | In terms of high frequency and low latency needs, less handshake is better. This is what QoS 0 mechanism is all about as a fire-and-forget process.|
| Actuator commands (safety-critical, exactly-once) | | |
| Backend service-to-service routing | | |
| OTA firmware delivery to constrained MCU (Class 2) | | |

### Detailed Justification

> *(Write 500–700 words here. Each recommendation must cite specific evidence — e.g. measured latency values from Section 5.1, packet overhead observed in Task 4, or implementation complexity experienced in Tasks 1–3.)*
> For the Sensor -> Cloud high frequency, low latency requirement I picked MQTT using QoS 0. The measurement of 0.7 ms in Section 5.1 already achieved the 100ms requirement. 

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
