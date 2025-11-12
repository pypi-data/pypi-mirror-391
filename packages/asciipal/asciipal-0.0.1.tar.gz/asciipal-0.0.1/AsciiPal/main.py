import random

# You can add as many of these as you want!
# Just make sure they are multi-line strings in the list.
ART_LIST = [
    r"""
  /\_/\
 ( o.o )
  > ^ <
""",
    r"""
   __
--(oo)
  (__)
""",
    r"""
(\__/)
(='.'=)
(")_(")
""",
    r"""
  / \
 / _ \
( ( ) )
 \_v_/
"""
]


def run():
    """
    This is the main entry point function for the 'asciipal' command.
    It prints a random piece of ASCII art from the list.
    """
    try:
        # Choose a random piece of art
        art = random.choice(ART_LIST)

        # Print it, removing any leading/trailing whitespace
        print(art.strip())

    except Exception as e:
        print(f"Oops! Something went wrong: {e}")


if __name__ == "__main__":
    # This allows you to test the script directly
    # by running `python asciipal/main.py`
    run()
