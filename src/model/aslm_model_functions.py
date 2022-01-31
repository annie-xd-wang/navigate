from model.concurrency.concurrency_tools import ObjectInSubprocess
import platform
import sys

def start_camera(configuration, camera_id, verbose):
    """
    # Initializes the camera as a sub-process using concurrency tools.
    """
    # Hamamatsu Camera
    if configuration.Devices['camera'] == 'HamamatsuOrca' and platform.system() == 'Windows':
        from model.devices.camera.Hamamatsu.HamamatsuCamera import Camera as CameraModel
        cam = ObjectInSubprocess(CameraModel, camera_id, verbose) #Do we still need to do this when we have the thread pool? Or do we need both? Have not investigated yet
        cam.initialize_camera()
        cam.set_exposure(configuration.CameraParameters['exposure_time'])
    elif configuration.Devices['camera'] == 'HamamatsuOrca' and platform.system() != 'Windows':
        print("Hamamatsu Camera is only supported on Windows operating systems.")
        sys.exit()
    elif configuration.Devices['camera'] == 'SyntheticCamera':
        from model.devices.camera.SyntheticCamera import Camera as CameraModel
        cam = CameraModel(0, verbose)
        cam.initialize_camera()
        cam.set_exposure(1000*configuration.CameraParameters['exposure_time'])
    else:
        print("Camera Type in Configuration.yml Not Recognized - Initialization Failed")
        sys.exit()
    if verbose:
        print("Initialized ", configuration.Devices['camera'])
    return cam

def start_stages(configuration, verbose):
    """
    # Initializes the Stage.
    """
    # Physik Instrumente Stage
    if configuration.Devices['stage'] == 'PI' and platform.system() == 'Windows':
        from model.devices.stages.PI.PIStage import Stage as StageModel
        stage = StageModel(configuration, verbose)
        stage.report_position()
    # Synthetic Stage
    elif configuration.Devices['stage'] == 'SyntheticStage':
        from model.devices.stages.SyntheticStage import Stage as StageModel
        stage = StageModel(configuration, verbose)
    else:
        print("Stage Type in Configuration.yml Not Recognized - Initialization Failed")
        sys.exit()
    if verbose:
        print("Initialized ", configuration.Devices['stage'])
    return stage

def start_zoom_servo(configuration, verbose):
    """
    # Initializes the Zoom Servo Motor. Dynamixel of SyntheticZoom
    """
    if configuration.Devices['zoom'] == 'Dynamixel':
        from model.devices.zoom.dynamixel.DynamixelZoom import Zoom as ZoomModel
        zoom = ZoomModel(configuration, verbose)
    elif configuration.Devices['zoom'] == 'SyntheticZoom':
        from model.devices.zoom.SyntheticZoom import Zoom as ZoomModel
        zoom = ZoomModel(configuration, verbose)
    else:
        print("Zoom Type in Configuration.yml Not Recognized - Initialization Failed")
        sys.exit()
    if verbose:
        print("Initialized ", configuration.Devices['zoom'])
        print("Zoom Position", zoom.read_position())
    return zoom

def start_filter_wheel(configuration, verbose):
    """
    # Initializes the Filter Wheel. Sutter or SyntheticFilterWheel
    """
    if configuration.Devices['filter_wheel'] == 'Sutter':
        from model.devices.filter_wheel.Sutter.Lambda10B import FilterWheel as FilterWheelModel
        filter_wheel = FilterWheelModel(configuration, verbose)
    elif configuration.Devices['filter_wheel'] == 'SyntheticFilterWheel':
        from model.devices.filter_wheel.SyntheticFilterWheel import SyntheticFilterWheel as FilterWheelModel
        filter_wheel = FilterWheelModel(configuration, verbose)
    else:
        print("Filter Wheel Type in Configuration.yml Not Recognized - Initialization Failed")
        sys.exit()
    if verbose:
        print("Initialized ", configuration.Devices['filter_wheel'])
    return filter_wheel

def start_lasers(configuration, verbose):
    '''
    # Start the lasers: Lasers or SyntheticLasers
    '''
    if configuration.Devices['lasers'] == 'Omicron':
        # This is the Omicron LightHUB Ultra Launch - consists of both Obis and Luxx lasers.
        from model.devices.lasers.coherent.ObisLaser import ObisLaser as obis
        from model.devices.lasers.omicron.LuxxLaser import LuxxLaser as luxx

        # Iteratively go through the configuration file and turn on each of the lasers,
        # and make sure that they are in appropriate external control mode.
        laser = {}
        for laser_idx in range(configuration.LaserParameters['number_of_lasers']):
            if laser_idx == 0:
                # 488 nm LuxX laser
                print("Initializing 488 nm LuxX Laser")
                comport = 'COM19'
                laser[laser_idx] = luxx(comport)
                laser[laser_idx].initialize_laser()

            elif laser_idx == 1:
                # 561 nm Obis laser
                print("Initializing 561 nm Obis Laser")
                comport = 'COM4'
                laser[laser_idx] = obis(comport)
                laser[laser_idx].set_laser_operating_mode('mixed')

            elif laser_idx == 2:
                # 642 nm LuxX laser
                print("Initializing 642 nm LuxX Laser")
                comport = 'COM17'
                laser[laser_idx] = luxx(comport)
                laser[laser_idx].initialize_laser()

            else:
                print("Laser index not recognized")
                sys.exit()

    elif configuration.Devices['lasers'] == 'SyntheticLasers':
        from model.devices.lasers.SyntheticLasers.SyntheticLasers import SyntheticLasers as SyntheticLasersModel
        laser = SyntheticLasersModel(configuration, verbose)

    else:
        print("Laser Type in Configuration.yml Not Recognized - Initialization Failed")
        sys.exit()

    if verbose:
        print("Initialized ", configuration.Devices['lasers'])

    return laser

def start_daq(configuration, etl_constants_path, verbose):
    """
    # Start the data acquisition device (DAQ):  NI or SyntheticDAQ
    """
    if configuration.Devices['daq'] == 'NI':
        from model.devices.daq.NI.NIDAQ import DAQ as DAQModel
        daq = DAQModel(configuration, etl_constants_path, verbose)
    elif configuration.Devices['daq'] == 'SyntheticDAQ':
        from model.devices.daq.SyntheticDAQ import DAQ as DAQModel
        daq = DAQModel(configuration, etl_constants_path, verbose)
    else:
        print("DAQ Type in Configuration.yml Not Recognized - Initialization Failed")
        sys.exit()
    if verbose:
        print("Initialized ", configuration.Devices['daq'])
    return daq


