"""
test_parabolic.py

Unit test for the ParabolicReflector class and the Tracer in the OPTICAL_RAY_COLLECTOR project.

This script checks:
1. Initialization of the Tracer.
2. Addition of a parabolic surface.
3. Generation of incident rays from a point light source.
4. Computation of intersections and reflected rays.
5. Recording of lighting scenes.

No visualization is included; this test is purely textual and serves to validate the core logic.
"""

if __name__ == "__main__":

    # Import required modules
    import pathlib
    import sys

    # Add the project root directory to sys.path for relative imports
    project_root = pathlib.Path(__file__).parent.parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from optical_ray_tracer.configurations.geometries import Parabolic   # ParabolicReflector class
    from optical_ray_tracer.rays.source import point_source              # Point light source
    from optical_ray_tracer.rays.raytracer import ray_tracer             # Main tracer engine

    # -----------------------------------------------
    # 1. Tracer Initialization
    # -----------------------------------------------
    print("Initializing the ray tracer...")
    tracer = ray_tracer.Tracer()
    
    # -----------------------------------------------
    # 2. Create and add a parabolic surface
    # -----------------------------------------------
    print("\nAdding optical surfaces...")

    parab = Parabolic.ParabolicReflector(surf_pos=[0, 0, 0])
    boundaries = parab.boundaries()
    print(f"Parabolic surface boundaries: {boundaries}")

    # Add the surface to the tracer
    surface_idx, _ = tracer.add_surface(
        str(parab.symbolic_equation()),  # Symbolic equation
        boundaries                       # Volume boundaries
    )
    print(f"Surface {surface_idx} added: {str(parab.symbolic_equation())}")

    # -----------------------------------------------
    # 3. Generate incident rays from the source
    # -----------------------------------------------
    print("\nGenerating incident rays from the source...")
    source = point_source.Source(position_x=0.0, position_y=0.0, position_z=15e8)
    n_rays = 10  # Number of rays to generate
    vec_dir, pt_orig = parab.generate_rays_from_source(n_rays, source)

    ray_idx, _ = tracer.add_rays(vec_dir, pt_orig)
    for i in range(len(vec_dir)):
        # ray_idx, _ = tracer.add_rays(vec_dir[i], pt_orig[i])
        print(f"Ray added (idx={i}): direction={vec_dir[i]}, origin={pt_orig[i]}")

    # -----------------------------------------------
    # 4. Compute intersections and reflections
    # -----------------------------------------------
    print("\nComputing intersections and reflections...")
    intersections, reflected = tracer.trace_new_scene()

    # -----------------------------------------------
    # 5. Display results
    # -----------------------------------------------
    print("\nResults:")
    
    print("Intersection points found:")
    for ray_idx, point in intersections.items():
        print(f"Ray {ray_idx}: intersection point = {point}")
    
    print("\nGenerated reflected rays:")
    for ray_idx, (dir_vec, origin) in reflected.items():
        print(f"Reflected ray {ray_idx}: direction={dir_vec}, origin={origin}")

    print("\nZippered rays for frontend")
    print(tracer.zippered_rays(pt_orig, list(intersections.values())))

    print("\nAnalysis of reflected rays on a plane")
    analyse_plane_pts = tracer.plane_analysis("XY", position=2, rays_dict=reflected)
    if len(reflected) == len(analyse_plane_pts):
        plot_pts = tracer.zippered_rays(list(intersections.values()), list(analyse_plane_pts.values()))
    else:
        # In case the number of intersection with the analysis plane is less than the number of reflected rays calculated
        origin_rescales = []
        for ray_idx, ray in analyse_plane_pts.items():
            origin_rescales.append(intersections[ray_idx])
        plot_pts = tracer.zippered_rays(origin_rescales, list(analyse_plane_pts.values()))
    print("\n Analysis on plane XY at 2m gives", len(plot_pts), "points")

    print("\nZ solve Symbolic equation")
    print("Z=",parab.solved_symbolic_equation())
    
    print("\nRecorded lighting scenes:")
    for i, scene in enumerate(tracer.lighting_scene):
        print(f"\nScene {i}:")
        for surf_idx, (inc_rays, refl_rays) in scene.items():
            print(f"Surface {surf_idx}:")
            print(f"  Number of incident rays: {len(inc_rays)}")
            print(f"  Number of reflected rays: {len(refl_rays)}")
