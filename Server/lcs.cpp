#include <iostream>
#include <vector>
#include <string>

std::string longest_common_substring(const std::vector<std::string>& strs) {
    if (strs.empty()) return "";
    int n = strs.size();
    int maxlen = 0;
    int end = 0;

    for (int i = 0; i < strs[0].size(); ++i) {
        for (int j = 0; j < strs[0].size(); ++j) {
            bool all_match = true;
            int k = 0;

            while (all_match && (k < n)) {
                if ((i + maxlen >= strs[k].size()) || (j + maxlen >= strs[0].size()) || (strs[k][i + maxlen] != strs[0][j + maxlen])) {
                    all_match = false;
                }
                ++k;
            }

            if (all_match) {
                end = j;
                ++maxlen;
            }
        }
    }
    return strs[0].substr(end - maxlen + 1, maxlen);
}

int main() {
    std::vector<std::string> strs;
    std::string line;
    while (std::getline(std::cin, line)) {
        strs.push_back(line);
    }
    
    std::cout << "Longest Common Substring: " << longest_common_substring(strs) << std::endl;
    return 0;
}
