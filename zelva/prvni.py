import turtle
import math
import random

def nakresli_ctverec(delka_strany):
    for _ in range(4):
        turtle.forward(delka_strany)
        turtle.left(90)

def domecek_jednim_tahem(delka_strany):
    # draws a square (base from current position, heading -> to the right)
    for _ in range(4):
        turtle.forward(delka_strany)
        turtle.left(90)
    # draw simple roof
    turtle.left(45)
    turtle.forward(delka_strany * (2 ** 0.5))
    turtle.left(90)
    turtle.forward(delka_strany * (2 ** 0.5) / 2)
    turtle.left(90)
    turtle.forward(delka_strany * (2 ** 0.5) / 2)
    turtle.left(90)
    turtle.forward(delka_strany * (2 ** 0.5))
    turtle.left(45)

def build_planet(diameter, n_houses):
    radius = diameter / 2
    
    # 1. Generate n random angles
    raw_angles = [random.uniform(0, 2 * math.pi) for _ in range(n_houses)]
    
    # 2. Sort them in REVERSE to create a CLOCKWISE path
    # This ensures the "Left" turns in the house function point OUTWARD
    angles = sorted(raw_angles, reverse=True)
    
    # 3. Convert angles to points
    points = []
    for angle in angles:
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))
        
    # 4. Draw the houses connecting the points
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)] # Wrap around to the first point
        
        # Calculate distance (size of house)
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        # Calculate Heading
        heading = math.degrees(math.atan2(dy, dx))
        
        # Move to position
        turtle.penup()
        turtle.goto(p1)
        turtle.setheading(heading)
        turtle.pendown()
        
        # Optional: Random colors to see them better
        turtle.pencolor(random.random(), random.random(), random.random())
        turtle.pensize(2)
        
        # Draw
        domecek_jednim_tahem(dist)

def main():
    screen = turtle.Screen()
    screen.bgcolor("black")
    screen.title("Clockwise Planet")
    
    turtle.speed(0)
    turtle.hideturtle()
    
    # You can change the diameter and number of houses here
    build_planet(diameter=300, n_houses=15)
    
    screen.exitonclick()

if __name__ == "__main__":
    main()