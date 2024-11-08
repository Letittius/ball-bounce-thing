import tkinter as tk
import math

# Create the main window
root = tk.Tk()
root.title("Ball with Momentum, Barrier Collision, and Blue Border")
root.geometry("800x800")
root.configure(bg="white")

# Define constants
BALL_SIZE = 30  # Diameter of the ball
GRAVITY = 1  # Gravity effect for bouncing
BOUNCE_DAMPING = 1  # Damping effect to reduce bounce height, closer to 1 for better ricochet
is_dropped = False  # To track if the ball was dropped
drawings = []  # List to keep track of drawings as barriers
draw_mode = False  # To toggle draw mode on and off

# Create a canvas to draw the ball, border, and handle drawing
canvas = tk.Canvas(root, width=800, height=800, bg="white", highlightthickness=0)
canvas.pack()

# Draw blue borders
canvas.create_line(0, 0, 800, 0, fill="blue", width=4)   # Top border
canvas.create_line(0, 800, 800, 800, fill="blue", width=4)  # Bottom border
canvas.create_line(0, 0, 0, 800, fill="blue", width=4)    # Left border
canvas.create_line(800, 0, 800, 800, fill="blue", width=4)  # Right border

# Create the ball at the center of the canvas
ball = canvas.create_oval(
    400 - BALL_SIZE // 2, 400 - BALL_SIZE // 2,
    400 + BALL_SIZE // 2, 400 + BALL_SIZE // 2,
    fill="red"
)

# Variables to track dragging and velocity
drag_data = {"x": 0, "y": 0, "vx": 0, "vy": 0}
velocity_y = 0  # Initial vertical velocity
velocity_x = 0

# Function to start dragging the ball with the left mouse button
def start_drag(event):
    global is_dropped
    if not draw_mode:  # Only drag if not in draw mode
        is_dropped = False  # Reset drop state
        drag_data["x"] = event.x
        drag_data["y"] = event.y
        drag_data["vx"] = 0
        drag_data["vy"] = 0

# Function to handle dragging the ball with the left mouse button
def on_drag(event):
    if not draw_mode:  # Only drag if not in draw mode
        # Calculate the new position
        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]

        # Move the ball by the drag amount
        canvas.move(ball, dx, dy)

        # Update drag data to calculate momentum for release
        drag_data["x"] = event.x
        drag_data["y"] = event.y
        drag_data["vx"] = dx / 2  # Set horizontal momentum
        drag_data["vy"] = dy / 2  # Set vertical momentum

# Function to drop the ball and make it bounce with momentum
def on_drop(event):
    global is_dropped, velocity_x, velocity_y
    if not draw_mode:  # Only drop if not in draw mode
        is_dropped = True  # Set the drop state
        velocity_x, velocity_y = drag_data["vx"], drag_data["vy"]
        bounce_ball()  # Start the bounce animation

# Function to incrementally move and bounce the ball off barriers
def bounce_ball():
    global velocity_y, velocity_x, is_dropped
    if is_dropped:
        x1, y1, x2, y2 = canvas.coords(ball)

        # Apply gravity to the vertical velocity
        velocity_y += GRAVITY

        # Move in small increments for precise collision detection
        steps = 10
        for _ in range(steps):
            # Calculate incremental movement
            new_x = x1 + (velocity_x / steps)
            new_y = y1 + (velocity_y / steps)

            # Check for collision with the window edges (blue borders)
            if new_y + BALL_SIZE >= 800:
                new_y = 800 - BALL_SIZE
                velocity_y = -velocity_y * BOUNCE_DAMPING
                if abs(velocity_y) < GRAVITY:
                    velocity_y = 0
                    is_dropped = False
            if new_y <= 0:
                new_y = 0
                velocity_y = -velocity_y * BOUNCE_DAMPING
            if new_x <= 0:
                new_x = 0
                velocity_x = -velocity_x * BOUNCE_DAMPING
            elif new_x + BALL_SIZE >= 800:
                new_x = 800 - BALL_SIZE
                velocity_x = -velocity_x * BOUNCE_DAMPING

            # Check for collisions with drawn barriers
            collided = False
            for line in drawings:
                if line_collision(new_x, new_y, line):
                    # Reflect both velocities based on collision direction
                    velocity_x, velocity_y = reflect_velocity(velocity_x, velocity_y, line)
                    collided = True
                    break

            if not collided:
                # Only update position if no collision detected
                canvas.coords(ball, new_x, new_y, new_x + BALL_SIZE, new_y + BALL_SIZE)
                x1, y1 = new_x, new_y  # Update x1, y1 for the next step

        # Schedule the next frame of the bounce animation
        root.after(20, bounce_ball)

# Function to detect collision between the ball and a drawn line
def line_collision(bx, by, line):
    # Get coordinates for the ball's center
    bx, by = bx + BALL_SIZE / 2, by + BALL_SIZE / 2

    # Get line segment coordinates
    x1, y1, x2, y2 = canvas.coords(line)

    # Calculate the closest point on the line to the ball's center
    line_len = math.hypot(x2 - x1, y2 - y1)
    dot_product = ((bx - x1) * (x2 - x1) + (by - y1) * (y2 - y1)) / line_len**2
    closest_x = x1 + dot_product * (x2 - x1)
    closest_y = y1 + dot_product * (y2 - y1)

    # Check if the distance from the ball's center to the closest point on the line is less than the ball's radius
    distance = math.hypot(bx - closest_x, by - closest_y)
    return distance <= BALL_SIZE / 2

# Function to reflect velocity based on the angle of the line it collides with
def reflect_velocity(vx, vy, line):
    x1, y1, x2, y2 = canvas.coords(line)

    # Calculate the normal vector of the line
    line_dx, line_dy = x2 - x1, y2 - y1
    length = math.hypot(line_dx, line_dy)
    nx, ny = -line_dy / length, line_dx / length  # Normal vector

    # Reflect the velocity using the normal vector and damping factor
    dot = vx * nx + vy * ny
    rx = vx - 2 * dot * nx
    ry = vy - 2 * dot * ny

    return rx * BOUNCE_DAMPING, ry * BOUNCE_DAMPING

# Function to toggle drawing mode
def toggle_draw_mode():
    global draw_mode
    draw_mode = not draw_mode  # Toggle draw mode
    draw_button.config(text="Drawing On" if draw_mode else "Drawing Off")  # Update button text

# Function to start drawing a continuous line with the left mouse button in draw mode
def start_drawing(event):
    if draw_mode:  # Only draw if in draw mode
        line = canvas.create_line(event.x, event.y, event.x, event.y, fill="black", width=2)
        drawings.append(line)  # Keep track of the line
        drag_data["x"] = event.x
        drag_data["y"] = event.y

# Function to continue drawing as the mouse is dragged
def draw(event):
    if draw_mode:  # Only draw if in draw mode
        x, y = drag_data["x"], drag_data["y"]
        # Update the last created line's endpoint as the mouse moves
        line = drawings[-1]
        canvas.coords(line, *canvas.coords(line)[:2], event.x, event.y)
        drag_data["x"] = event.x
        drag_data["y"] = event.y

# Function to erase all drawings
def erase_drawings():
    for drawing in drawings:
        canvas.delete(drawing)
    drawings.clear()  # Clear the list of drawings

# Create the "Erase" button to clear all drawings
erase_button = tk.Button(root, text="Erase", bg="blue", fg="white", command=erase_drawings)
erase_button.pack(pady=10)

# Create the "Draw Mode" toggle button to enable or disable drawing
draw_button = tk.Button(root, text="Drawing Off", bg="red", fg="white", command=toggle_draw_mode)
draw_button.pack(pady=10)

# Bind the events to the ball for dragging and dropping with the left mouse button
canvas.tag_bind(ball, "<Button-1>", start_drag)
canvas.tag_bind(ball, "<B1-Motion>", on_drag)
canvas.tag_bind(ball, "<ButtonRelease-1>", on_drop)

# Bind the events for continuous drawing with the left mouse button (if in draw mode)
canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw)

# Run the tkinter loop to display the window
root.mainloop()
#win