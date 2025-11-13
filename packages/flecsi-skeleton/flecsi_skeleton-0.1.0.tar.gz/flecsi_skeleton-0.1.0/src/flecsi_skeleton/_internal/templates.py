################################################################################
# CMakeLists
################################################################################

#------------------------------------------------------------------------------#
# Top-Level CMakeLists.txt
#------------------------------------------------------------------------------#

TOPLEVEL_CMAKELISTS = """\
#------------------------------------------------------------------------------#
# Top-Level CMakeLists.txt
#------------------------------------------------------------------------------#

cmake_minimum_required(VERSION 3.20)

project({UCC_APPNAME} LANGUAGES C CXX)

set(CMAKE_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_EXTENSIONS OFF)

#------------------------------------------------------------------------------#
# Find FleCSI package.
#------------------------------------------------------------------------------#

find_package(FleCSI 2 REQUIRED)

#------------------------------------------------------------------------------#
# Formatting
#
# FleCSI provides several cmake convenience utilities. This section adds
# a formatting target `make format` using clang-format. You can change the
# formatting style by editing {LC_APPNAME}/.clang-format.
#------------------------------------------------------------------------------#

option(ENABLE_FORMAT "Enable format target" OFF)
mark_as_advanced(ENABLE_FORMAT)

if(ENABLE_FORMAT)
  include(FleCSI/format)

  set(CLANG_FORMAT_VERSION "18...<19" CACHE STRING
      "Set the required version (major[.minor[.patch]]) of clang-format")
  mark_as_advanced(CLANG_FORMAT_VERSION)

  flecsi_add_format_target(${{PROJECT_NAME}} ${{PROJECT_SOURCE_DIR}}
    "${{CLANG_FORMAT_VERSION}}")
endif()

  #----------------------------------------------------------------------------#
  # Set floating-point precision.
  #----------------------------------------------------------------------------#

  set(CONFIG_PRECISIONS double float)
  if(NOT CONFIG_PRECISION)
    list(GET CONFIG_PRECISIONS 0 CONFIG_PRECISION)
  endif()

  set(CONFIG_PRECISION "${{CONFIG_PRECISION}}" CACHE STRING
    "Select the floating-point precision")
  set_property(CACHE CONFIG_PRECISION PROPERTY STRINGS ${{CONFIG_PRECISIONS}})
  set(Config_PRECISION "${{CONFIG_PRECISION}}")
  mark_as_advanced(CONFIG_PRECISION)

#------------------------------------------------------------------------------#
# Add library.
#------------------------------------------------------------------------------#

set(SPEC_TARGET "${{CMAKE_PROJECT_NAME}}-Spec")
add_library(${{SPEC_TARGET}} INTERFACE)
add_library(${{SPEC_TARGET}}::${{SPEC_TARGET}} ALIAS ${{SPEC_TARGET}})
target_include_directories(${{SPEC_TARGET}}
  INTERFACE
    $<BUILD_INTERFACE:${{CMAKE_CURRENT_SOURCE_DIR}}>
    $<BUILD_INTERFACE:${{CMAKE_BINARY_DIR}}>
    $<INSTALL_INTERFACE:${{CMAKE_INSTALL_INCLUDEDIR}}>
)
add_subdirectory(spec)

#------------------------------------------------------------------------------#
# Config Header
#------------------------------------------------------------------------------#

configure_file(${{PROJECT_SOURCE_DIR}}/spec/config.hh.in
  ${{CMAKE_BINARY_DIR}}/spec/config.hh @ONLY)

#------------------------------------------------------------------------------#
# Add application.
#------------------------------------------------------------------------------#

add_subdirectory(app)
"""

#------------------------------------------------------------------------------#
# Specialization CMakeLists.txt
#------------------------------------------------------------------------------#

SPEC_CMAKELISTS = """\
#------------------------------------------------------------------------------#
# Specialization CMakeLists.txt
#------------------------------------------------------------------------------#

function(spec_headers)
  target_sources(${{SPEC_TARGET}} PUBLIC FILE_SET public_headers TYPE HEADERS
    BASE_DIRS ${{CMAKE_SOURCE_DIR}} FILES ${{ARGN}})
endfunction()

spec_headers(
  control.hh
)
"""

#------------------------------------------------------------------------------#
# Application CMakeLists.txt
#------------------------------------------------------------------------------#

APP_CMAKELISTS = """\
#------------------------------------------------------------------------------#
# {UCC_APPNAME} CMakeLists.txt
#------------------------------------------------------------------------------#

option({UC_APPNAME}_WRITE_CONTROL_INFO
  "Output the control model graph and actions at startup"
  FleCSI_ENABLE_GRAPHVIZ)
mark_as_advanced({UC_APPNAME}_WRITE_CONTROL_INFO)

add_executable({LC_APPNAME} {LC_APPNAME}.cc)
target_link_libraries({LC_APPNAME} ${{SPEC_TARGET}}::${{SPEC_TARGET}} FleCSI::FleCSI)

if(FleCSI_ENABLE_GRAPHVIZ AND {UC_APPNAME}_WRITE_CONTROL_INFO)
  target_compile_definitions({LC_APPNAME} PUBLIC {UC_APPNAME}_WRITE_CONTROL_INFO)
elseif(NOT FleCSI_ENABLE_GRAPHVIZ AND {UC_APPNAME}_WRITE_CONTROL_INFO)
  message(WARNING,
    "{UC_APPNAME}_WRITE_CONTROL_INFO enabled but FleCSI not compiled with Graphviz")
endif()
"""

################################################################################
# Specialization source
################################################################################

#------------------------------------------------------------------------------#
# Config
#------------------------------------------------------------------------------#

SPEC_CONFIG = """\
#ifndef SPEC_CONFIG_HH
#define SPEC_CONFIG_HH

namespace cfg {{

using precision = @CONFIG_PRECISION@;

}}

#endif // SPEC_CONFIG_HH
"""

#------------------------------------------------------------------------------#
# Control Model
#------------------------------------------------------------------------------#

SPEC_CONTROL = """\
#ifndef SPEC_CONTROL_HH
#define SPEC_CONTROL_HH

#include <flecsi/flog.hh>
#include <flecsi/run/control.hh>

namespace spec::control {{
/// Control Points.
enum class cp {{
  /// Application initialization.
  initialize,
  /// Time evolution (cycled).
  advance,
  /// Running analysis (cycled).
  analyze,
  /// Application finalization.
  finalize
}};

inline const char *
operator*(cp control_point) {{
  switch(control_point) {{
    case cp::initialize:
      return "initialize";
    case cp::advance:
      return "advance";
    case cp::analyze:
      return "analyze";
    case cp::finalize:
      return "finalize";
  }}
  flog_fatal("invalid control point");
}}

template<typename S>
struct control_policy : flecsi::run::control_base {{

  using control_points_enum = cp;

  /// Control Model Constructor
  /// @param steps Maximum number of time steps.
  /// @param log   Logging frequency.
  control_policy(std::size_t steps, std::size_t log)
    : steps_(steps), log_(log) {{}}

  S & state() {{
    return state_;
  }}
  auto step() const {{
    return step_;
  }}
  auto steps() const {{
    return steps_;
  }}
  auto log() const {{
    return log_;
  }}

  static bool cycle_control(control_policy & cp) {{
    return cp.step_++ < cp.steps_ && S::cycle_control(cp);
  }}

  using evolve = cycle<cycle_control, point<cp::advance>, point<cp::analyze>>;

  using control_points =
    list<point<cp::initialize>, evolve, point<cp::finalize>>;

protected:
  S state_;
  std::size_t step_{{0}};
  std::size_t steps_;
  std::size_t log_;
}};
}} // namespace spec::control

#endif // SPEC_CONTROL_HH
"""

#------------------------------------------------------------------------------#
# Exports
#------------------------------------------------------------------------------#

SPEC_EXPORTS = """\
#ifndef SPEC_EXPORTS_HH
#define SPEC_EXPORTS_HH

#include "types.hh"

namespace spec::type::exports {{

namespace ft = spec::ft;

using spec::na, spec::ro, spec::wo, spec::rw;

using spec::field;
using spec::global;
using spec::single;

}} // namespace spec::type::exports

namespace spec::exports {{
using namespace spec::type::exports;
}} // namespace spec::exports

#endif // SPEC_EXPORTS_HH
"""

#------------------------------------------------------------------------------#
# Types
#------------------------------------------------------------------------------#

SPEC_TYPES = """\
#ifndef SPEC_TYPES_HH
#define SPEC_TYPES_HH

#include <spec/config.hh>

#include <flecsi/data.hh>

namespace spec {{

namespace ft {{
using real_t = cfg::precision;
}} // namespace ft

// Concise privileges
inline constexpr flecsi::privilege na = flecsi::na, ro = flecsi::ro,
                                   wo = flecsi::wo, rw = flecsi::rw;

using flecsi::field;
using flecsi::topo::global;
template<typename T>
using single = field<T, flecsi::data::single>;

}} // namespace spec

#endif // SPEC_TYPES_HH
"""

################################################################################
# Application source
################################################################################

#------------------------------------------------------------------------------#
# Driver
#------------------------------------------------------------------------------#

APP_DRIVER = """\
/*----------------------------------------------------------------------------*
  Driver (main function)
 *----------------------------------------------------------------------------*/

// These import the action definitions.
#include "advance.hh"
#include "analyze.hh"
#include "finalize.hh"
#include "initialize.hh"
#include "state.hh"

/*
  Headers are ordered by decreasing locality, e.g., directory, project,
  library dependency, standard library.
 */
#include "types.hh"

#include <spec/control.hh>

#include <flecsi/runtime.hh>

using namespace flecsi;
using namespace {LC_APPNAME};

int
main(int argc, char ** argv) {{
  // Output control model information.
#if defined({UC_APPNAME}_WRITE_CONTROL_INFO)
  {LC_APPNAME}::control::write_graph("{UC_APPNAME}", "cm.dot");
  {LC_APPNAME}::control::write_actions("{UC_APPNAME}", "actions.dot");
#endif

  const flecsi::getopt g;
  try {{
    g(argc, argv);
  }}
  catch(const std::logic_error & e) {{
    std::cerr << e.what() << ' ' << g.usage(argc ? argv[0] : "");
    return 1;
  }}

  const run::dependencies_guard dg;
  run::config cfg;

  runtime run(cfg);
  flog::add_output_stream("clog", std::clog, true);
  run.control<control<state>>(10, 1);
}}
"""

#------------------------------------------------------------------------------#
# Advance
#------------------------------------------------------------------------------#

APP_ADVANCE = """\
#ifndef {UC_APPNAME}_ADVANCE_HH
#define {UC_APPNAME}_ADVANCE_HH

#include "state.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
advance(control_policy<state> & cp) {{
  flog(info) << "Advance Action: " << cp.step() << std::endl;
}}

inline control<state>::action<advance, cp::advance> advance_action;
}} // namespace {LC_APPNAME}::action

#endif // {UC_APPNAME}_ADVANCE_HH
"""

#------------------------------------------------------------------------------#
# Analyze
#------------------------------------------------------------------------------#

APP_ANALYZE = """\
#ifndef {UC_APPNAME}_ANALYZE_HH
#define {UC_APPNAME}_ANALYZE_HH

#include "state.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
analyze(control_policy<state> & cp) {{
  flog(info) << "Analyze Action: " << cp.step() << std::endl;
}}

inline control<state>::action<analyze, cp::analyze> analyze_action;
}} // namespace {LC_APPNAME}::action

#endif // {UC_APPNAME}_ANALYZE_HH
"""

#------------------------------------------------------------------------------#
# Finalize
#------------------------------------------------------------------------------#

APP_FINALIZE = """\
#ifndef {UC_APPNAME}_FINALIZE_HH
#define {UC_APPNAME}_FINALIZE_HH

#include "state.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
finalize(control_policy<state> &) {{
  flog(info) << "Finalize Action" << std::endl;
}}

inline control<state>::action<finalize, cp::finalize> final_action;
}} // namespace {LC_APPNAME}::action

#endif // {UC_APPNAME}_FINALIZE_HH
"""

#------------------------------------------------------------------------------#
# Initialize
#------------------------------------------------------------------------------#

APP_INITIALIZE = """\
#ifndef {UC_APPNAME}_INITIALIZE_HH
#define {UC_APPNAME}_INITIALIZE_HH

#include "state.hh"
#include "tasks/initialize.hh"

#include <flecsi/flog.hh>

namespace {LC_APPNAME}::action {{

void
initialize(control_policy<state> & cp) {{
  auto & s = cp.state();
  auto & sch = cp.scheduler();

  flog(info) << "Initialize Action" << std::endl;

  // Allocate global topology to processes() (default behavior of {{}})
  sch.allocate(s.gt, {{}});

  // Initialize time variables
  sch.template execute<tasks::init::time_vars>(s.t(*s.gt),
    s.dt(*s.gt), 0.0);
}}

inline control<state>::action<initialize, cp::initialize> init_action;
}} // namespace {LC_APPNAME}::action

#endif // {UC_APPNAME}_INITIALIZE_HH
"""

#------------------------------------------------------------------------------#
# State
#------------------------------------------------------------------------------#

APP_STATE = """\
#ifndef {UC_APPNAME}_STATE_HH
#define {UC_APPNAME}_STATE_HH

#include "types.hh"

namespace {LC_APPNAME} {{

struct state {{

  /*--------------------------------------------------------------------------*
    Topology pointers.
   *--------------------------------------------------------------------------*/

  global::ptr gt; /* Global topology. */

  /*--------------------------------------------------------------------------*
    Global parameters.
   *--------------------------------------------------------------------------*/

  static inline const single<double>::definition<global> t, dt;

  /*--------------------------------------------------------------------------*
    Cycle control.
   *--------------------------------------------------------------------------*/

  static void advance(single<ft::real_t>::accessor<rw> t,
    single<ft::real_t>::accessor<rw> dt) noexcept {{
    const ft::real_t tf{{1.0}};
    dt = *dt;
    dt = t + dt > tf ? tf - t : dt;
    t += dt;
  }}

  static bool cycle_control(control_policy<state> & cp) {{
    auto & s = cp.state();
    auto & sch = cp.scheduler();
    sch.template execute<advance>(s.t(*s.gt), s.dt(*s.gt));
    return true;
  }}
}};

}} // namespace {LC_APPNAME}

#endif // {UC_APPNAME}_STATE_HH
"""

#------------------------------------------------------------------------------#
# Types
#------------------------------------------------------------------------------#

APP_TYPES = """\
#ifndef {UC_APPNAME}_TYPES_HH
#define {UC_APPNAME}_TYPES_HH

#include <spec/control.hh>
#include <spec/exports.hh>

namespace {LC_APPNAME} {{

using namespace spec::exports;

template<typename S>
using control_policy = spec::control::control_policy<S>;
template<typename S>
using control = flecsi::run::control<control_policy<S>>;
using cp = spec::control::cp;

}} // namespace {LC_APPNAME}

#endif // {UC_APPNAME}_TYPES_HH
"""

################################################################################
# Application tasks
################################################################################

APP_TASK_INITIALIZE = """\
#ifndef {UC_APPNAME}_TASKS_INITIALIZE_HH
#define {UC_APPNAME}_TASKS_INITIALIZE_HH

#include "../types.hh"

namespace {LC_APPNAME}::tasks::init {{

void inline time_vars(single<ft::real_t>::accessor<wo> t,
  single<ft::real_t>::accessor<wo> dt,
  ft::real_t t0) noexcept {{
  t = t0;
  dt = 0.1;
}}

}} // namespace {LC_APPNAME}::tasks::init

#endif // {UC_APPNAME}_TASKS_INITIALIZE_HH
"""
