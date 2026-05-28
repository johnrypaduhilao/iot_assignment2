# Module 1 Assignment — Protocol Comparison Report

**Student Name:** Johnry Christian Paduhilao
**Student ID:**   101002576
**Date:**        May 28, 2026

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
   > Honestly on my actual results above, I could not see lost messages for QoS 0 but upon checking the result from tshark captures, QoS 0 didn't use any handshake which means there is no acknowledgement. So if this is applied in real-world, QoS 0 is deployed in a lossy network there would be no mechanism to detect or recover dropped messages resulting in lost messages.

2. **QoS 1 may show duplicates. Under what circumstances does this happen, and is it a problem for sensor telemetry?** *(2–3 sentences)*

   > QoS 1 uses publish & puback handshake where duplicates can happen when puback is lost. One more thing I can support is the DUP flag in the fixed-header byte (33) shown in section 4.2, which was 0 here because nothing was retransmitted but will happen in real-world IoT applications. For sensor telemetry purposes repeated reading is harmless because the next reading will just replace the current one.

3. **QoS 2 has higher latency than QoS 1. What causes this, and when is the trade-off worth it?** *(2–3 sentences)*

   > QoS2 has visible latency above of 1.3 (almost double with QoS 0 & 1) which is mainly because it is doing a four-message handshake: publish, pubrec, pubrel and pubcomp unlike QoS 0 and 1 which uses simpler deliveries. To elaborate further these extra steps make it more resilient but also means more latency is visible. This trade-off is worth it especially in safety-critical systems that may cause an actual harm to the users.

---

## 5.2 CoAP–HTTP Proxy Mapping

> Run `pytest tests/coap/test_proxy.py -v -s` and record the observed HTTP headers.

| HTTP Header | CoAP Option | Your Observed Value |
|-------------|-------------|---------------------|
| Content-Type | Content-Format (12) | application/json which is the interpretation for CoAP Content Format (50) that server returns |
| Cache-Control: max-age | Max-Age (14) | Max-Age will be 60 since this is the default value if not overridden which our server did not. |
| ETag | ETag (4) | None. Server did not set any ETags |
| Location | Location-Path (8) | None. This only appears if we use resources that uses POST specifically 2.01 Created. Because we used GET automatically there is None. |

---

## 5.3 Protocol Selection Recommendation

*(500–700 words. Justify each recommendation with specific technical evidence from your implementation and packet captures.)*

### Data Path Recommendations

| Data Path | Recommended Protocol | Justification |
|-----------|---------------------|---------------|
| Sensor → Cloud (high frequency, <100 ms latency) | MQTT using QoS 0 | In terms of high frequency and low latency needs, fewer handshakes are better. This is what QoS 0 mechanism is all about as a fire-and-forget process.|
| Actuator commands (safety-critical, exactly-once) | MQTT QoS 2 | In terms of safety critical applications, four-message handshake: publish, pubrec, pubrel and pubcomp is required for exactly-once delivery. As a trade-off there is more latency but necessary cost to ensure no duplication. |
| Backend service-to-service routing | #1 AMQP, #2 MQTT QoS 1 | In terms of concept this is the best for the said data-path because apart from topic exchanges and publish confirmations like MQTT and CoAP, AMQP has durable queues and dead-letter exchanges which is specifically designed for server to server backend integration. If I need to exclude AMQP then MQTT QoS 1 with persistent connection lacks durable queues and dead letter exchanges. |
| OTA firmware delivery to constrained MCU (Class 2) | CoAP (Block2) | Class 2 device has around 50 KB RAM, 250 KB flash so CoAP's compact 4-byte fixed header and UDP-based stateless model means a much smaller code footprint than MQTT's TCP-based broker connection. |

### Detailed Justification

> For the Sensor -> Cloud high frequency, low latency requirement I picked MQTT using QoS 0. The measurement of 0.7 ms in Section 5.1 is well under the 100 ms requirement. While both QoS 0 and QoS 1 achieved the same required latency, QoS 0 is much faster because there is no acknowledgment, as evidenced by filtering the pcap (tshark -r captures/mqtt.pcap -Y "mqtt.msgtype == 3 && mqtt.qos == 0") showing no PUBACK frames follow the QoS 0 publishes. To support this claim, Section 4.2 annotation showed that QoS 1 is always paired with PUBACK frame and QoS 2 has much greater latency in 5.1 table because of additional handshake steps. This also means that QoS 0 is less reliable than QoS 1 and 2 but that is the trade-off for a need of high frequency and low latency system. For the Actuator commands (safety-critical, exactly-once), I picked MQTT QoS 2. This is because of the four-message handshake publish, pubrec, pubrel, and pubcomp which prioritizes reliability over low latency processes. As evidence, filtering the pcap with tshark -r captures/mqtt.pcap -Y 'mqtt.msgtype == 5' reveals the Publish Received (id=2051) frame — the PUBREC packet that begins the four-step handshake. The measured latency of 1.3 ms (Section 5.1), roughly double QoS 0/1, is a tolerable cost for the safety guarantee. This matters because for a cooling-fan actuator, a lost ON command could leave the production line overheating, while a duplicated command (which QoS 1 may produce per Section 5.1 Q2) could cause the fan to oscillate or override a later OFF which both are unacceptable failure modes for safety-critical hardware. QoS 0 fails on loss and QoS 1 fails on duplication, only QoS 2 prevents both of them. For Backend service-to-service routing data path, AMQP is more suitable than the other two in terms of its specifications and concept. Its strength is that it is specifically designed for server to server backend integration because of durable queues and dead-letter exchanges. As a support evidence, the Task 3 specifications in the starter kit described the following: iot.telemetry topic exchange, iot.dlx direct exchange, queue bindings, TTL, max length which are the patterns for a robust backend service integration designed for distributed systems. As a fallback for AMQP, MQTT QoS 1 is a good option for service to service routing. The factory/{line}/{sensor} hierarchy gives topic-based routing that backend services can subscribe to with wildcards and the broker fans messages out to multiple subscribers. For OTA firmware delivery to constrained MCU (Class 2), I picked CoAP with Block-wise transfer (Block2) as the perfect candidate. Class 2 devices have small RAM and flash which means the CoAP's compact design, specifically Block-wise transfer (Block2), matches the needs of constrained devices. To support the claim, In Section 4.3 I annotated byte 0 (0x42) of a CoAP packet, showing the protocol's compact 4-byte fixed header, which combined with UDP's stateless model gives a smaller memory footprint than MQTT's TCP-based broker connection. UDP datagrams on constrained 6LoWPAN networks are practically limited to ~1280 bytes. Along with CoAP's Block2 option it splits a large response into numbered blocks the client reassembles. As evidence, My ManifestResource (in src/coap/server.py) returns a 50-entry JSON firmware manifest, and the observer reassembled it as a 10,771-byte payload across multiple Block2 blocks.
---

## 5.4 Reflection

*(300–400 words addressing all three prompts below.)*

### Technical Challenge

> The whole setup process caused me to do different ways to run the code because of package mismatch. And one of the most technical challenges I encountered is working on the CoAP test which directly links up to the package mismatch I mentioned during setup. The pytest-asyncio version causes errors every time I ran the 10 CoAP server tests specifically showing "future attached to a different loop" error. I re-installed all packages again and just found out that my py-test asyncio is using 1.3.0 instead of pulling specific package 0.21.2. I also found out that the starter kit's tests uses an older pattern that newer pytest-asyncio deprecated. This caused the fixture's loop and the test method's loop to be different which is connected to the package mismatch.

### Most Surprising Protocol Difference

> The most surprising difference was CoAP's compact header. I was amazed by how CoAP header is only 4 bytes for the whole header value which I annotated in 4.3. At first, I was in disbelief and re-checked and it was truly a difference maker especially for edge devices or federated learning, which requires lightweight techniques to implement. This surprise made me realize a real protocol difference against MQTT which can be tied back to the last recommendation I mentioned in the earlier section 5.3 specifically stating the header efficiency as why CoAP is the right choice for Class 2 devices which has small memory capability. In contrast, every MQTT packet in my pcap carried roughly 40 bytes of TCP/IP framing on top of its own bytes which is a substantial overhead on a constrained 6LoWPAN network where the practical MTU is only ~1280 bytes. 

### Most Complex Protocol to Implement

> CoAP because of async programming which is unfamiliar compared to synchronous code. CoAP uses aiocoap APIs which I need to be specifically knowledgeable of asyncio and await processes. Also to add time.sleep will not work which I am not able to figure out early because it freezes the whole thread rather than asyncio.sleep which is limited to a specific task. I would also add the required understanding of the patterns like async for response in pr.observation, sequence number tracking and clean deregistration. Also to add is the Block 2 reassembly as another concept piece I mentioned in section 5.3 which actually contributes about how to split a >3KB response into numbered chunks and the client reassembles, which is conceptually different from MQTT or HTTP's send-the-whole-body model.

---

*Module 1 Assignment — Real-Time Data Analytics for IoT*
