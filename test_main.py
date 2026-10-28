import sys
sys.argv = ['main.py', '--scenario', 'straight', '--traffic-density', '0.1', '--fusion-range', '50.0', '--fusion-fov', '180.0']

# Import and run main
from src.main import main
main()