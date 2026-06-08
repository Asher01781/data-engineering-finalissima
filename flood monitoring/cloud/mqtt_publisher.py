import json
import random
import time


class CloudPublisher:
    """
    Simulates cloud publishing via MQTT.

    Lab 4:
    - Fault tolerance
    - Exponential backoff retry
    - Local cache fallback

    Lab 5:
    - Efficient Edge Transport
    - Payload serialization
    - Payload size monitoring

    Lab 14:
    - MQTT cloud publishing
    """

    def publish(self, payload):
        # Lab 5: Payload Serialization
        payload_json = json.dumps(payload)
        full_size = len(
            payload_json.encode("utf-8")
        )
        # Compact transport format
        compact_payload = {
            "ts": payload["timestamp"],
            "wl": payload["water_level"],
            "obj": payload["object_count"]
        }
        compact_json = json.dumps(
            compact_payload
        )
        compact_size = len(
            compact_json.encode("utf-8")
        )
        print(
            f"[TRANSPORT] "
            f"{full_size} -> {compact_size} bytes"
        )


        # Lab 4: Fault Tolerance + Retry
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Simulated network reliability
                success = (
                    random.random() > 0.2
                )
                if not success:
                    raise ConnectionError(
                        "MQTT connection failed"
                    )
                print(
                    "[MQTT]",
                    payload
                )
                return True

            except Exception:
                wait_time = 2 ** retry
                print(
                    f"[RETRY] "
                    f"Attempt "
                    f"{retry + 1}/"
                    f"{max_retries}"
                    f" | Waiting "
                    f"{wait_time}s"
                )
                time.sleep(wait_time)


        # Lab 4: Local Cache Fallback
        print(
            "[CACHE]",
            payload
        )
        with open(
            "local.jsonl",
            "a"
        ) as f:
            f.write(
                payload_json + "\n"
            )
        return False