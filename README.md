# Module 1 Assignment — SmartFactory IoT Protocol Integration

**Student Name:** Johnry Christian Paduhilao
**Student ID:**   101002576
**Date:**        May 28, 2026

---

**Real-Time Data Analytics for IoT** · Graduate Course · Module 1

---

## Quick Start

```bash
#Some steps are updated due to fix local machine's package issues . Added a tag (ADDED!) as my personal added step

# 1. Start Docker services (Mosquitto for MQTT) (ADDED!) 
docker compose up -d mosquitto rabbitmq

# 2. Install dependencies and start Docker services
#bash setup.sh <- ORIGINAL Step 2
python3 -m venv .venv #(ADDED!) 
source .venv/bin/activate #(ADDED!) 
pip install --upgrade pip #(ADDED!) 
pip install -r requirements.txt #(ADDED!) 


# 3. Read the full assignment specification
refer to Module1_Assignment.docx for the full specification

# 4. Work through the tasks in order:
#    Task 1 → src/mqtt/publisher.py  + src/mqtt/subscriber.py
#    Task 2 → src/coap/server.py     + src/coap/observer.py
#    Task 3 → src/amqp/topology.py   + src/amqp/producer.py   + src/amqp/consumer.py
#    Task 4 → bash scripts/capture.sh → annotate report/packet_analysis.md
#    Task 5 → report/comparison_report.md 

# 5. Run all tests before submitting (AMQP tests are expected to fail because it is not implemented.)
pytest tests/ -v --tb=short 
```

---

## Repository Structure

```
module1-assignment/
├── src/
│   ├── mqtt/
│   │   ├── publisher.py      ← Task 1.1  Fill in all TODO sections
│   │   └── subscriber.py     ← Task 1.2  Fill in all TODO sections
│   ├── coap/
│   │   ├── server.py         ← Task 2.1  Fill in all TODO sections
│   │   └── observer.py       ← Task 2.2  Fill in all TODO sections
│   └── amqp/
│       ├── topology.py       ← Task 3.1  Fill in all TODO sections
│       ├── producer.py       ← Task 3.2  Fill in all TODO sections
│       └── consumer.py       ← Task 3.3  Fill in all TODO sections
│
├── tests/
│   ├── mqtt/
│   │   ├── test_publisher.py   ← Do not modify
│   │   └── test_qos_loss.py    ← Do not modify (run with -s for output table)
│   ├── coap/
│   │   └── test_server.py      ← Do not modify
|   |   └── test_proxy.py       ← THIS FILE WAS NON EXISTENT, Created personally to perform 2.3 TASK
│   └── amqp/
│       └── test_topology.py    ← Do not modify
│
├── report/
│   ├── packet_analysis.md    ← Task 4  Fill in the annotation tables
│   └── comparison_report.md  ← Task 5  Write your analysis here
│
├── captures/                 ← Task 4  pcap files go here (git-ignored)
├── scripts/
│   └── capture.sh            ← Task 4  Run to capture traffic
├── config/
│   └── mosquitto.conf        ← Mosquitto broker configuration
├── docker-compose.yml        ← Infrastructure: Mosquitto + RabbitMQ + InfluxDB
├── requirements.txt
├── pytest.ini
└── setup.sh                  ← Run this first
```

---

## Running Individual Components

```bash
# Task 1 — MQTT
python -m src.mqtt.publisher       # Terminal 1
python -m src.mqtt.subscriber      # Terminal 2

# Task 2 — CoAP
python -m src.coap.server          # Terminal 1
python -m src.coap.observer        # Terminal 2

# Task 3 — AMQP (run in order)
python -m src.amqp.topology        # Once — sets up RabbitMQ topology
python -m src.amqp.producer        # Terminal 1
python -m src.amqp.consumer        # Terminal 2

# Task 4 — Packet capture (with publisher/server running)
bash scripts/capture.sh
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Individual task tests
pytest tests/mqtt/ -v
pytest tests/coap/ -v
pytest tests/amqp/ -v

# QoS experiment with output table (Task 1.3)
pytest tests/mqtt/test_qos_loss.py -v -s
```

---

## Infrastructure

| Service | Port | URL |
|---------|------|-----|
| Mosquitto MQTT | 1883 | mqtt://localhost:1883 |
| RabbitMQ AMQP | 5672 | amqp://localhost:5672 |
| RabbitMQ Management | 15672 | http://localhost:15672 (guest/guest) |
| CoAP server (Python) | 5683 | coap://localhost:5683 |
| InfluxDB (optional) | 8086 | http://localhost:8086 |

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f mosquitto
docker compose logs -f rabbitmq
```

---

## Submission Checklist

Before zipping and submitting:

- [ ] All 7 source files have TODO sections completed (Ignored AMQP per instructions)
- [ ] `pytest tests/ -v` passes (or partial passes documented) (Except AMQP)
- [ ] `captures/` contains mqtt.pcap, coap.pcap, amqp.pcap (Ignored AMQP per instructions)
- [x] `report/packet_analysis.md` — all annotation tables filled in
- [x] `report/comparison_report.md` — all sections written (1500–2000 words total)
- [x] README.md updated with your name and any notes for the marker

---

## Important Notes
- Task 3 (AMQP) and Section 4.4 omitted per professor instructions;
  src/amqp/*.py files remain as unmodified skeletons
- tests/coap/test_proxy.py written by me (was missing from the starter kit)
- Task 1.3 referenced "analysis questions in the starter kit" but no separate file
  was distributed;
- pytest-asyncio pinned to 0.21.2 in requirements.txt; newer versions deprecate
  the kit's fixture pattern and break the CoAP tests

*Graduate Course: Real-Time Data Analytics for IoT · Module 1*
