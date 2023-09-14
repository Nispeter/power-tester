// C++ program to demonstrate descending order sort using
// greater<>().
#include <bits/stdc++.h>
using namespace std;

int main()
{
        const int SIZE = 5000;
        int numbers[SIZE];
        srand(static_cast<unsigned int>(std::time(nullptr)));
        for (int i = 0; i < SIZE; ++i) numbers[i] = rand()%100;
	sort(numbers, numbers + SIZE, greater<int>());


	return 0;
}