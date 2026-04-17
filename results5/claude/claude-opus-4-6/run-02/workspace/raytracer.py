#!/usr/bin/env python3
"""A from-scratch ray tracer that renders a scene with reflections, shadows, and a checkered floor."""

import math
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, o: "Vec3") -> "Vec3":
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: "Vec3") -> "Vec3":
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s: float) -> "Vec3":
        return Vec3(self.x * s, self.y * s, self.z * s)

    def __rmul__(self, s: float) -> "Vec3":
        return self.__mul__(s)

    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    def dot(self, o: "Vec3") -> float:
        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o: "Vec3") -> "Vec3":
        return Vec3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )

    def length(self) -> float:
        return math.sqrt(self.dot(self))

    def normalized(self) -> "Vec3":
        n = self.length()
        if n == 0:
            return Vec3()
        return self * (1.0 / n)

    def hadamard(self, o: "Vec3") -> "Vec3":
        return Vec3(self.x * o.x, self.y * o.y, self.z * o.z)

    def reflect(self, normal: "Vec3") -> "Vec3":
        return self - 2.0 * self.dot(normal) * normal

    def clamp01(self) -> "Vec3":
        return Vec3(
            max(0.0, min(1.0, self.x)),
            max(0.0, min(1.0, self.y)),
            max(0.0, min(1.0, self.z)),
        )


@dataclass
class Ray:
    origin: Vec3
    direction: Vec3


@dataclass
class Material:
    color: Vec3
    ambient: float = 0.1
    diffuse: float = 0.7
    specular: float = 0.5
    shininess: float = 64.0
    reflectivity: float = 0.0


@dataclass
class HitRecord:
    t: float
    point: Vec3
    normal: Vec3
    material: Material


class Sphere:
    def __init__(self, center: Vec3, radius: float, material: Material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray: Ray) -> Optional[HitRecord]:
        oc = ray.origin - self.center
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        sqrt_d = math.sqrt(discriminant)
        t = (-b - sqrt_d) / (2.0 * a)
        if t < 0.001:
            t = (-b + sqrt_d) / (2.0 * a)
        if t < 0.001:
            return None
        point = ray.origin + ray.direction * t
        normal = (point - self.center).normalized()
        return HitRecord(t, point, normal, self.material)


class Plane:
    def __init__(self, point: Vec3, normal: Vec3, material: Material, checkered: bool = False):
        self.point = point
        self.normal = normal.normalized()
        self.material = material
        self.checkered = checkered

    def intersect(self, ray: Ray) -> Optional[HitRecord]:
        denom = self.normal.dot(ray.direction)
        if abs(denom) < 1e-6:
            return None
        t = (self.point - ray.origin).dot(self.normal) / denom
        if t < 0.001:
            return None
        hit_point = ray.origin + ray.direction * t
        mat = self.material
        if self.checkered:
            fx = math.floor(hit_point.x * 0.5)
            fz = math.floor(hit_point.z * 0.5)
            if (int(fx) + int(fz)) % 2 == 0:
                mat = Material(
                    color=Vec3(0.95, 0.95, 0.95),
                    ambient=mat.ambient,
                    diffuse=mat.diffuse,
                    specular=mat.specular * 0.3,
                    shininess=mat.shininess,
                    reflectivity=mat.reflectivity,
                )
        return HitRecord(t, hit_point, self.normal, mat)


@dataclass
class PointLight:
    position: Vec3
    color: Vec3
    intensity: float = 1.0


class Scene:
    def __init__(self):
        self.objects: list = []
        self.lights: list[PointLight] = []
        self.bg_top = Vec3(0.4, 0.6, 1.0)
        self.bg_bottom = Vec3(0.85, 0.9, 1.0)

    def add(self, obj):
        self.objects.append(obj)

    def add_light(self, light: PointLight):
        self.lights.append(light)

    def background(self, ray: Ray) -> Vec3:
        t = 0.5 * (ray.direction.normalized().y + 1.0)
        return self.bg_bottom * (1.0 - t) + self.bg_top * t

    def closest_hit(self, ray: Ray) -> Optional[HitRecord]:
        closest: Optional[HitRecord] = None
        for obj in self.objects:
            hit = obj.intersect(ray)
            if hit and (closest is None or hit.t < closest.t):
                closest = hit
        return closest

    def is_shadowed(self, point: Vec3, light_pos: Vec3) -> bool:
        to_light = light_pos - point
        dist = to_light.length()
        shadow_ray = Ray(point, to_light.normalized())
        hit = self.closest_hit(shadow_ray)
        return hit is not None and hit.t < dist

    def shade(self, ray: Ray, hit: HitRecord, depth: int) -> Vec3:
        mat = hit.material
        result = mat.color * mat.ambient

        for light in self.lights:
            if self.is_shadowed(hit.point, light.position):
                continue

            to_light = (light.position - hit.point).normalized()
            n_dot_l = max(0.0, hit.normal.dot(to_light))
            diff = mat.color * (mat.diffuse * n_dot_l * light.intensity)

            view_dir = -ray.direction.normalized()
            half_vec = (to_light + view_dir).normalized()
            n_dot_h = max(0.0, hit.normal.dot(half_vec))
            spec_strength = math.pow(n_dot_h, mat.shininess) if n_dot_h > 0 else 0.0
            spec = light.color * (mat.specular * spec_strength * light.intensity)

            result = result + diff + spec

        if mat.reflectivity > 0.0 and depth > 0:
            reflect_dir = ray.direction.normalized().reflect(hit.normal)
            reflect_ray = Ray(hit.point, reflect_dir)
            reflected_color = self.trace(reflect_ray, depth - 1)
            result = result * (1.0 - mat.reflectivity) + reflected_color * mat.reflectivity

        return result

    def trace(self, ray: Ray, depth: int = 5) -> Vec3:
        hit = self.closest_hit(ray)
        if hit is None:
            return self.background(ray)
        return self.shade(ray, hit, depth)


def build_scene() -> Scene:
    scene = Scene()

    scene.add(Plane(
        Vec3(0, -0.5, 0), Vec3(0, 1, 0),
        Material(color=Vec3(0.3, 0.3, 0.35), diffuse=0.6, specular=0.2, shininess=16, reflectivity=0.15),
        checkered=True,
    ))

    scene.add(Sphere(
        Vec3(0, 0.5, -3), 1.0,
        Material(color=Vec3(0.8, 0.2, 0.2), diffuse=0.8, specular=0.9, shininess=128, reflectivity=0.3),
    ))

    scene.add(Sphere(
        Vec3(-2.2, 0.2, -4), 0.7,
        Material(color=Vec3(0.2, 0.8, 0.3), diffuse=0.7, specular=0.6, shininess=64, reflectivity=0.15),
    ))

    scene.add(Sphere(
        Vec3(2.0, 0.0, -2.5), 0.5,
        Material(color=Vec3(0.2, 0.4, 0.9), diffuse=0.7, specular=0.8, shininess=96, reflectivity=0.2),
    ))

    scene.add(Sphere(
        Vec3(-0.8, -0.15, -1.5), 0.35,
        Material(color=Vec3(0.9, 0.7, 0.1), diffuse=0.8, specular=0.9, shininess=128, reflectivity=0.4),
    ))

    scene.add(Sphere(
        Vec3(1.0, -0.25, -1.8), 0.25,
        Material(color=Vec3(0.7, 0.2, 0.8), diffuse=0.7, specular=0.7, shininess=64, reflectivity=0.1),
    ))

    scene.add_light(PointLight(Vec3(-5, 8, -2), Vec3(1, 1, 1), 0.8))
    scene.add_light(PointLight(Vec3(5, 6, -1), Vec3(1, 0.95, 0.85), 0.5))
    scene.add_light(PointLight(Vec3(0, 3, 2), Vec3(0.85, 0.9, 1.0), 0.3))

    return scene


def render(width: int, height: int, scene: Scene) -> list[list[Vec3]]:
    aspect = width / height
    fov = math.pi / 3
    half_w = math.tan(fov / 2)
    half_h = half_w / aspect

    camera_pos = Vec3(0, 1.5, 3)
    look_at = Vec3(0, 0.2, -2)
    up = Vec3(0, 1, 0)

    forward = (look_at - camera_pos).normalized()
    right = forward.cross(up).normalized()
    cam_up = right.cross(forward).normalized()

    pixels: list[list[Vec3]] = []
    total = height
    for j in range(height):
        row: list[Vec3] = []
        if j % 50 == 0:
            pct = j / total * 100
            print(f"\rRendering... {pct:.0f}%", end="", flush=True, file=sys.stderr)
        for i in range(width):
            color = Vec3()
            samples = 4
            for si in range(2):
                for sj in range(2):
                    u = (2 * (i + (si + 0.5) / 2) / width - 1) * half_w
                    v = (1 - 2 * (j + (sj + 0.5) / 2) / height) * half_h
                    direction = (forward + right * u + cam_up * v).normalized()
                    ray = Ray(camera_pos, direction)
                    color = color + scene.trace(ray)
            color = color * (1.0 / samples)
            row.append(color.clamp01())
        pixels.append(row)

    print("\rRendering... 100%", file=sys.stderr)
    return pixels


def gamma_correct(c: float) -> int:
    return max(0, min(255, int(math.pow(c, 1.0 / 2.2) * 255 + 0.5)))


def write_ppm(filename: str, pixels: list[list[Vec3]]):
    height = len(pixels)
    width = len(pixels[0])
    with open(filename, "w") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for row in pixels:
            for p in row:
                r = gamma_correct(p.x)
                g = gamma_correct(p.y)
                b = gamma_correct(p.z)
                f.write(f"{r} {g} {b} ")
            f.write("\n")


def main():
    width, height = 800, 500

    if len(sys.argv) > 1:
        try:
            w, h = sys.argv[1].split("x")
            width, height = int(w), int(h)
        except ValueError:
            pass

    output = "scene.ppm"
    if len(sys.argv) > 2:
        output = sys.argv[2]

    print(f"Ray tracer — rendering {width}x{height} with 4x AA", file=sys.stderr)
    scene = build_scene()
    pixels = render(width, height, scene)
    write_ppm(output, pixels)
    print(f"Saved to {output}", file=sys.stderr)

    try:
        from subprocess import run as sp_run
        sp_run(["convert", output, output.replace(".ppm", ".png")], capture_output=True)
        print(f"Also converted to {output.replace('.ppm', '.png')}", file=sys.stderr)
    except Exception:
        pass


if __name__ == "__main__":
    main()
