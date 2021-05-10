#include <iostream>
#include <cmath>

using namespace std;


signed main(int argc, char const *argv[])
{
	int n;
	cin >> n;
	for (int d = pow(10, n - 1), d < pow(10, n), ++d) {
		bool p = true;
		for (int i = 2; i * i <= d; ++i) {
			if (!(d%i)) {
				p = false;
				break;
			}
		}
		if (p) {
			cout << d;
			exit(0);
		}
	}
	return 0;
}