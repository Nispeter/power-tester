#include <iostream>
#include <vector>
#include <algorithm>
#include <sstream>

int main() {
    std::string line;
    std::vector<int> numbers;
    int number;

    // Read a line of input
    std::getline(std::cin, line);
    std::istringstream iss(line);

    // Extract numbers from the line and add to the vector
    while (iss >> number) {
        numbers.push_back(number);
    }

    // Sort the numbers
    std::sort(numbers.begin(), numbers.end());


    return 0;
}
