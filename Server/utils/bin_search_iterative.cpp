#include <iostream>
#include <vector>
#include <cstdlib> // for atoi


int binarySearchIterative(const std::vector<int>& arr, int target) {
    int low = 0;
    int high = arr.size() - 1;

    while (low <= high) {
        int mid = low + (high - low) / 2;

        if (arr[mid] == target) {
            return mid;
        } else if (arr[mid] < target) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }
    return -1;
}


int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " target num1 num2 num3 ..." << std::endl;
        return 1;
    }

    // First command-line argument is the target
    int target = std::atoi(argv[1]);

    // Rest of the arguments form the array
    std::vector<int> arr;
    for (int i = 2; i < argc; i++) {
        arr.push_back(std::atoi(argv[i]));
    }

    int resultIterative = binarySearchIterative(arr, target);


    return 0;
}
