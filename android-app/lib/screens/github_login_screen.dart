// github_login_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_web_auth/flutter_web_auth.dart';
import 'package:provider/provider.dart';
import '../services/auth_service.dart';
import 'home_screen.dart';

class GitHubLoginScreen extends StatelessWidget {
  const GitHubLoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ربط GitHub')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('سيتم توجيهك إلى GitHub للموافقة على الصلاحيات.'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                // بدء عملية OAuth
                final url = 'http://your-backend.com/api/auth/github/login'; // استبدل بالرابط الفعلي
                final result = await FlutterWebAuth.authenticate(
                  url: url,
                  callbackUrlScheme: 'myapp',
                );

                // result سيكون شيئاً مثل myapp://callback?token=...
                final token = Uri.parse(result).queryParameters['token'];
                if (token != null) {
                  final auth = Provider.of<AuthService>(context, listen: false);
                  await auth.saveToken(token);
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => const HomeScreen()),
                  );
                }
              },
              child: const Text('متابعة إلى GitHub'),
            ),
          ],
        ),
      ),
    );
  }
}
