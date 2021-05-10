import java.util.Scanner;

public class Task2 {
	public static void main(String[] args) {
		Scanner scan = new Scanner(System.in);
		int n = scan.nextInt();
		int ans = 0;
		for (int i = 0; i < n; ++i) {
			int a = scan.nextInt();
			ans += a;
		}
		System.out.print(ans);
	}
}