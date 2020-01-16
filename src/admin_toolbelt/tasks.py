import dramatiq

from .storage import create_path


def set_actor_queue(actor, queue_name):
    actor.broker.declare_queue(queue_name)
    actor.queue_name = queue_name

create_path = dramatiq.actor(create_path)
