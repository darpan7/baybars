# Copyright 2018 Jet.com 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

# Local
from .timber import get_logger
# 3rd Party
from confluent_kafka import KafkaException, Producer

DEFAULT_TIMEOUT_IN_MILLISECONDS = 100


def value_serializer(payload: dict):
  return json.dumps(payload).encode('utf-8')


class KafkaPublisher:
  def __init__(self, 
               kafka_endpoint, 
               kafka_topic_name, 
               serializer=value_serializer, 
               timeout_ms=DEFAULT_TIMEOUT_IN_MILLISECONDS):
    self.kafka_endpoint = kafka_endpoint
    self.kafka_topic_name = kafka_topic_name
    bootstrap_servers = {'bootstrap.servers': self.kafka_endpoint}
    self.producer = Producer(bootstrap_servers)
    self.serializer = serializer
    self.logger = get_logger('{}'.format(self.kafka_topic_name))

  def delivery_callback(self, err, msg):
        '''
        Default kafka callback function.
        It is triggered by poll() or flush() \n
        when a message has been successfully delivered
        or permanently failed delivery (after retries).
        '''
        if err:
            # Kafka permanently failed to produce message.
            raise KafkaException(
                'Kafka delivery failed permanently. Reason: {}'.format(err)
            )

  def publish(self, message, key=None, call_back=None):
    self.producer.produce(
        self.kafka_topic_name, 
        self.serializer(message),
        key,
        callback=call_back or self.delivery_callback
      )
    out = self.producer.flush()
    return out

  def publish_batch(self, messages):
    out = [self.publish(message) for message in messages]
    self.producer.flush()
    return out
