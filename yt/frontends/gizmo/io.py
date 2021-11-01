from yt.frontends.gadget.io import IOHandlerGadgetHDF5


class IOHandlerGizmo(IOHandlerGadgetHDF5):
    _dataset_type = "gizmo_hdf5"
    _vector_fields = {
        "Coordinates": 3,
        "Velocity": 3,
        "Velocities": 3,
        "MagneticField": 3,
        "FourMetalFractions": 4,
        "PhotonEnergy": 5,
    }
