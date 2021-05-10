#include <iostream>

using namespace std;


signed main(int argc, char const *argv[])
{
	int n, m;
	cin>>n>>m;
	int d=1;
	for(int i = 0; i < n; ++i) {
		for (int j = 0; j < m; ++j) {
			cout << d <<' ';
			d++;
		}
		cout<<'\n';
	}
	return 0;
}
