#include <stdio.h>


int main(int argc, char const *argv[])
{

	int n;
	scanf("%d", &n);
	int ans = 0;
	for (int i = 0; i < n; ++i) {
		int a;
		scanf("%d", &a);
		ans += a;
	}
	printf("%d", ans);
	return 0;
}
