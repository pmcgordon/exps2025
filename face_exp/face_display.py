import os
import random
import pygame
import time
import csv

def get_image_files():
    # Get paths to image directories
    current_dir = os.getcwd()
    different_dir = os.path.join(current_dir, 'jpeg', 'different')
    same_dir = os.path.join(current_dir, 'jpeg', 'same')

    # Get all jpeg files and attach folder code
    # Folder code: 1 = same, 0 = different (per user request)
    different_files = [(os.path.join(different_dir, f), 0) for f in os.listdir(different_dir) if f.endswith('.jpg')]
    same_files = [(os.path.join(same_dir, f), 1) for f in os.listdir(same_dir) if f.endswith('.jpg')]

    # Combine and shuffle
    all_files = different_files + same_files
    random.shuffle(all_files)
    return all_files

def display_images(image_files):
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Face Display")
    
    results = []
    
    for image_path, folder_code in image_files:
        # Load and display image
        image = pygame.image.load(image_path)
        image = pygame.transform.scale(image, (600, 400))  # Adjust size as needed
        
        # Center the image
        image_rect = image.get_rect()
        image_rect.center = screen.get_rect().center
        
        # Display image
        screen.fill((255, 255, 255))  # White background
        screen.blit(image, image_rect)
        pygame.display.flip()
        
        # Wait for input or timeout
        start_time = time.time()
        key_pressed = None

        while time.time() - start_time < 8 and key_pressed is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Allow user to close window
                    pygame.quit()
                    return results
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SLASH:
                        key_pressed = '/'
                    elif event.key == pygame.K_z:
                        key_pressed = 'z'

        # Map key to response code: '/' -> 1, 'z' -> 0, timeout -> None
        if key_pressed == '/':
            response_code = 1
        elif key_pressed == 'z':
            response_code = 0
        else:
            response_code = None

        results.append((image_path, folder_code, response_code))
    
    pygame.quit()
    return results

def write_results(results):
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Write results to CSV
    csv_path = os.path.join('data', 'test.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        # Header: Image, Folder (1=same,0=different), Response (1='/',0='z')
        writer.writerow(['Image', 'Folder', 'Response'])
        for image_path, folder_code, response_code in results:
            writer.writerow([os.path.basename(image_path), folder_code, response_code if response_code is not None else ''])

    # Compute and display statistics
    # Exclude timeouts (response_code is None) from percent correct and contingency
    total = 0
    correct = 0
    timeouts = 0
    # contingency[true_status][response] where true_status and response are 0 or 1
    contingency = [[0, 0], [0, 0]]

    for _, folder_code, response_code in results:
        if response_code is None:
            timeouts += 1
            continue
        total += 1
        if response_code == folder_code:
            correct += 1
        contingency[folder_code][response_code] += 1

    if total > 0:
        percent_correct = 100.0 * correct / total
    else:
        percent_correct = float('nan')

    print(f"Results written to: {csv_path}")
    print(f"Trials counted (excluding {timeouts} timeouts): {total}")
    if not (percent_correct != percent_correct):  # not NaN
        print(f"Percent correct: {percent_correct:.2f}% ({correct}/{total})")
    else:
        print("Percent correct: N/A (no non-timeout trials)")

    # Print contingency table
    print('\nContingency table (rows=true status: 0=different,1=same; columns=response: 0=z/different,1=/=same)')
    print('       Response=0    Response=1')
    print(f"True=0   {contingency[0][0]:>10} {contingency[0][1]:>12}")
    print(f"True=1   {contingency[1][0]:>10} {contingency[1][1]:>12}")

def main():
    image_files = get_image_files()
    results = display_images(image_files)
    write_results(results)

if __name__ == "__main__":
    main()
