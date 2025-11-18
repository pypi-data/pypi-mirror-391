#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// Conditional real-SDK integration.
#ifdef DJI_SDK_AVAILABLE
#include <DJI_SDK.h> // expected to be provided by the user / SDK installation
#endif

// Helpers to build a python-friendly dict
static py::dict make_attitude(double q0, double q1, double q2, double q3) {
    py::dict d;
    d["q0"] = q0;
    d["q1"] = q1;
    d["q2"] = q2;
    d["q3"] = q3;
    return d;
}

static py::dict make_position(double lat, double lon, double alt) {
    py::dict d;
    d["lat"] = lat;
    d["lon"] = lon;
    d["alt"] = alt;
    return d;
}

#ifdef DJI_SDK_AVAILABLE
// Real SDK-backed implementations. The exact SDK function names and signatures
// will depend on the DJI SDK you use; adapt these wrappers to match the SDK.
static bool activate_real(py::object app_id, py::object app_key, py::object api_level) {
    // Example placeholder: call a C function DJI_Activate if available.
    // Users should replace DJI_Activate with the actual SDK call.
    (void)app_id; (void)app_key; (void)api_level;
    return DJI_Activate() == 0;
}

static py::dict get_broadcast_real() {
    py::dict out;
    // Example placeholder structure; replace with SDK calls that populate these fields.
    dji_broadcast_t b;
    DJI_GetBroadcast(&b);
    out["attitude"] = make_attitude(b.q0, b.q1, b.q2, b.q3);
    out["position"] = make_position(b.lat, b.lon, b.alt);
    py::dict vel;
    vel["vx"] = b.vx; vel["vy"] = b.vy; vel["vz"] = b.vz;
    out["velocity"] = vel;
    py::dict rc;
    rc["pitch"] = b.rc_pitch; rc["roll"] = b.rc_roll; rc["yaw"] = b.rc_yaw; rc["throttle"] = b.rc_throttle;
    out["rc"] = rc;
    out["battery"] = b.battery;
    return out;
}

static bool takeoff_real() { return DJI_Takeoff() == 0; }
static bool land_real() { return DJI_Land() == 0; }
static bool rth_real() { return DJI_ReturnToHome() == 0; }
static bool upload_mission_real(py::list items) {
    // Convert python list to SDK structure as needed.
    (void)items;
    return DJI_UploadMission() == 0;
}
static bool start_mission_real(int mission_id, int start_seq) {
    return DJI_StartMission(mission_id, start_seq) == 0;
}
static bool pause_mission_real() { return DJI_PauseMission() == 0; }
static bool gimbal_control_real(double pitch, double roll, double yaw) {
    return DJI_GimbalControl(pitch, roll, yaw) == 0;
}
static bool set_rc_override_real(py::dict channels) {
    (void)channels;
    return DJI_SetRCOverride() == 0;
}

static bool control_management_real(bool obtain) {
    DJI_Pro_Control_Type t = obtain ? TAKE_OFF_CONTROL : RELEASE_CONTROL;
    return DJI_Pro_Control_Management(t) == 0;
}
#endif

// Stub implementations used when no real SDK is linked
static bool activate_stub(py::object app_id, py::object app_key, py::object api_level) {
    (void)app_id; (void)app_key; (void)api_level;
    return true;
}

static py::dict get_broadcast_stub() {
    py::dict d;
    d["attitude"] = make_attitude(1.0, 0.0, 0.0, 0.0);
    d["position"] = make_position(0.0, 0.0, 0.0);
    py::dict vel;
    vel["vx"] = 0.0; vel["vy"] = 0.0; vel["vz"] = 0.0;
    d["velocity"] = vel;
    py::dict rc;
    rc["pitch"] = 0; rc["roll"] = 0; rc["yaw"] = 0; rc["throttle"] = 0;
    d["rc"] = rc;
    d["battery"] = 100.0;
    py::dict ctrl;
    ctrl["id"] = 2;
    ctrl["label"] = "onboard";
    d["ctrl_device"] = ctrl;
    d["flight_status"] = 0;
    d["display_mode"] = 0;
    return d;
}

static bool takeoff_stub() { return true; }
static bool land_stub() { return true; }
static bool rth_stub() { return true; }
static bool upload_mission_stub(py::list items) { (void)items; return true; }
static bool start_mission_stub(int mission_id, int start_seq) { (void)mission_id; (void)start_seq; return true; }
static bool pause_mission_stub() { return true; }
static bool gimbal_control_stub(double pitch, double roll, double yaw) { (void)pitch; (void)roll; (void)yaw; return true; }
static bool set_rc_override_stub(py::dict channels) { (void)channels; return true; }
static bool control_management_stub(bool obtain) { (void)obtain; return true; }

PYBIND11_MODULE(_djibindings, m) {
    m.doc() = "DJI SDK binding (conditional real-SDK integration)";
#ifdef DJI_SDK_AVAILABLE
    m.def("activate", &activate_real, "Activate the DJI SDK", py::arg("app_id")=py::none(), py::arg("app_key")=py::none(), py::arg("api_level")=py::none());
    m.def("get_broadcast", &get_broadcast_real, "Get broadcast telemetry as a dict");
    m.def("takeoff", &takeoff_real);
    m.def("land", &land_real);
    m.def("return_to_home", &rth_real);
    m.def("upload_mission", &upload_mission_real);
    m.def("start_mission", &start_mission_real, py::arg("mission_id")=0, py::arg("start_seq")=0);
    m.def("pause_mission", &pause_mission_real);
    m.def("gimbal_control", &gimbal_control_real, py::arg("pitch")=0.0, py::arg("roll")=0.0, py::arg("yaw")=0.0);
    m.def("set_rc_override", &set_rc_override_real);
    m.def("control_management", &control_management_real, py::arg("obtain")=true);
#else
    m.def("activate", &activate_stub, "Activate the DJI SDK", py::arg("app_id")=py::none(), py::arg("app_key")=py::none(), py::arg("api_level")=py::none());
    m.def("get_broadcast", &get_broadcast_stub, "Get broadcast telemetry as a dict");
    m.def("takeoff", &takeoff_stub);
    m.def("land", &land_stub);
    m.def("return_to_home", &rth_stub);
    m.def("upload_mission", &upload_mission_stub);
    m.def("start_mission", &start_mission_stub, py::arg("mission_id")=0, py::arg("start_seq")=0);
    m.def("pause_mission", &pause_mission_stub);
    m.def("gimbal_control", &gimbal_control_stub, py::arg("pitch")=0.0, py::arg("roll")=0.0, py::arg("yaw")=0.0);
    m.def("set_rc_override", &set_rc_override_stub);
    m.def("control_management", &control_management_stub, py::arg("obtain")=true);
#endif
}


