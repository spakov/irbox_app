"""
Count generator routine, used for message count.
"""

# A reasonably large number of messages before resetting to 0
COUNT_MAX = 65535

def count_generator():
    """
    Message count generator.
    """
    while True:
        for i in range(COUNT_MAX):
            yield i
