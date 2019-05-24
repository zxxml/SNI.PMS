namespace SNI {
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Linq;
    using System.Reflection;
    using System.Security.Cryptography;
    using System.Text;
    using BCrypt.Net;

    internal class Utilities {
        internal static string HashSha256(string text) {
            var textBytes = Encoding.UTF8.GetBytes(text);
            var textSha256 = SHA256.Create().ComputeHash(textBytes);
            return Convert.ToBase64String(textSha256);
        }

        internal static string HashPwd(string password) {
            var pwdSha256 = HashSha256(password);
            return BCrypt.HashPassword(pwdSha256);
        }

        internal static bool CheckPwd(string password, string pwdHashed) {
            var pwdSha256 = HashSha256(password);
            return BCrypt.Verify(pwdSha256, pwdHashed);
        }
    }

    internal static class ToDictHelper {
        internal static IDictionary<string, object> ToDict(this object obj) {
            var dictionary = new Dictionary<string, object>();
            var bindingFlags = BindingFlags.Public | BindingFlags.Instance;
            return obj.GetType().GetProperties(bindingFlags).ToDictionary(
                propInfo => propInfo.Name,
                propInfo => propInfo.GetValue(obj, null));
        }
    }

    internal static class Extensions {
        internal static Dictionary<string, object> ToDict(this object obj, bool nullable = false) {
            var dict = new Dictionary<string, object>();
            var properties = obj.GetType().GetProperties(BindingFlags.Public | BindingFlags.Instance);
            foreach (var property in properties) {
                var method = property.GetGetMethod();
                if (method != null && method.IsPublic) {
                    var value = method.Invoke(obj, new object[] { });
                    if (nullable || value != null) {
                        dict.Add(property.Name, value);
                    }
                }
            }
        }
    }
}