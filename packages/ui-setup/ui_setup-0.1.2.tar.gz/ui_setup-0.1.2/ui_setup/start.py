import argparse
import logging
from .features.clone_ui import clone_ui
from .tools import load_settings
from .ui import show_title, show_info
from .onboarding import onboard

def setup_debug_logging(debug: bool) -> None:
  if debug:
    logging.basicConfig(
      level=logging.DEBUG,
      format='%(name)s - %(levelname)s - %(message)s',
      force=True
    )

def main():
  parser = argparse.ArgumentParser(description='UI Setup')
  parser.add_argument('--debug', action='store_true', help='Enable debug logging')
  args = parser.parse_args()

  setup_debug_logging(args.debug)

  show_title()

  try:
    load_settings()
  except FileNotFoundError:
    show_info("Looks like it's your first time here. Welcome!", "info")
    onboard()
    show_title()
  clone_ui()

if __name__ == "__main__":
  main()