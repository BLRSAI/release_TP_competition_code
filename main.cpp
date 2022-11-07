#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include <string>
#include <cstring>
#include <cassert>

#include "pros/apix.h"
#include "main.h"

// Identifiers for debugging purposes
#define BRAIN_IDENTIFIER "B "
#define JETSON_IDENTIFIER 'J'

#define GPS_PORT 17

char data_received[50];
char previous_data_received[50];
float velocity = 0.0;
float rotation = 0.0;

double slew(double target_speed, double step, double current_speed)
{

    if (fabs(current_speed) > fabs(target_speed))
        step = 200;

    if (target_speed > current_speed + step)
        current_speed += step;
    else if (target_speed < current_speed - step)
        current_speed -= step;
    else
        current_speed = target_speed;

    return current_speed;
}

// Credited to: https://stackoverflow.com/questions/9210528/split-string-with-delimiters-in-c
char** str_split(char* a_str, const char a_delim)
{
    char** result    = 0;
    size_t count     = 0;
    char* tmp        = a_str;
    char* last_comma = 0;
    char delim[2];
    delim[0] = a_delim;
    delim[1] = 0;

    /* Count how many elements will be extracted. */
    while (*tmp)
    {
        if (a_delim == *tmp)
        {
            count++;
            last_comma = tmp;
        }
        tmp++;
    }

    /* Add space for trailing token. */
    count += last_comma < (a_str + strlen(a_str) - 1);

    /* Add space for terminating null string so caller
       knows where the list of returned strings ends. */
    count++;

    result = (char**)malloc(sizeof(char*) * count);

    if (result)
    {
        size_t idx  = 0;
        char* token = strtok(a_str, delim);

        while (token)
        {
            assert(idx < count);
            *(result + idx++) = strdup(token);
            token = strtok(0, delim);
        }
        assert(idx == count - 1);
        *(result + idx) = 0;
    }

    return result;
}

// Reads data being sent from the Jetson
bool read_from_jetson()
{
    char** parsed_data_received;
    fgets(data_received, sizeof(data_received), stdin);

    if (strcmp(data_received, previous_data_received) != 0)
    {
        parsed_data_received = str_split(data_received, ' ');
        velocity = atof(parsed_data_received[1]) * 40;
        rotation = atof(parsed_data_received[2]) * 40;

        strcpy(previous_data_received, data_received);
        return true;
    }
    return false;
}

/* Writes the brain data to the Jetson.
 * printf is used here as when using pros because
 * printf redirects data from stdout to the pros terminal.
 * This is how writing to the brain functions so simply */
void write_to_brain(std::string data)
{
    data = BRAIN_IDENTIFIER + data + "\n";
    printf("%s", data.c_str());
}

// Initalizes the motors on the robot
void initialize()
{
    pros::lcd::initialize();
    double tpu = 35;

    chassis::init({-8, -9, 10}, {-1, 2, 3}, // motors
            600,                     // gearset
            tpu, 4.00,               // TPU
            12,                      // setle time
            2, 1,                    // linear/angular thresholds
            8, 2,                    // regular/arc slew
            0,                       // imu port
            {0, 0, 0},               // encoder ports
            0,                       // expander port
            0                       // joystick threshold
            );

    odom::init(false, 0, 0, tpu, tpu,
            false, // holonomic
            10     // exit error
            );

    pid::init(false,       // debug
            0.28, 0, .6, // linear
            1, 0, 3,     // angular
            3.5, 0, 1,   // linear point
            50, 0, 0,    // angular point
            .05,         // arc
            .75,         // dif
            5            // min error
            );

    // // initialize subsystems
    intake::init();
    lift::init();
}

void autonomous()
{
}

// Gets the time since the robot first moves
double get_game_time(std::uint32_t inital_time)
{
    return (pros::millis() - inital_time) / 1000;
}

// This is run after the autonomous period
void opcontrol()
{
    double left_previous = 0;
    double right_previous = 0;
    double right_speed = 0;
    double left_speed = 0;
    bool jetson_writing = true;
    bool first_run = true;
    std::string gps_data;
    std::string data;
    std::uint32_t inital_time;
    int i = 0;

    // Initalizes the GPS sensor
    pros::Gps gps1(GPS_PORT);
    pros::c::gps_status_s_t status;

    while (true)
    {
        // Gets the current x and y coordinates of the robot from the GPS sensor
        status = gps1.get_status();

        // Concatenating the string that holds the data that needs to be sent to the Jetson
        gps_data = std::to_string(status.x) + " " + std::to_string(status.y);
        data = std::to_string(get_game_time(inital_time)) + " " + gps_data + " " + std::to_string(0)
            + " " + std::to_string(0) + " " + std::to_string(i);

        /* If the jetson have received new data then its state will be changed to write,
         * if it has just written data it will be set to its reading state */
        if (jetson_writing)
        {
            write_to_brain(data.c_str());
            jetson_writing = false;
        }
        else
        {
            jetson_writing = read_from_jetson();
        }

        // Calculates the speed in which the right and left side of the robot need to move
        right_speed = velocity - rotation;
        left_speed = velocity + rotation;

        // Slewing produces smoother movement results
        left_speed = slew(left_speed, 8, left_previous);
        right_speed = slew(right_speed, 8, right_previous);

        // Starts the intake and zeros the time
        if (velocity != 0 && first_run)
        {
            intake::move(100);
            inital_time = pros::millis();
            first_run = false;
        }

        // Moves the robot based on the calculated speeds of each side
        chassis::tank(left_speed, right_speed);

        // Saved old values for slew calculations
        left_previous = left_speed;
        right_previous = right_speed;
        i++;
    }
}
