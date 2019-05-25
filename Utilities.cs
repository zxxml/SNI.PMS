using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;

namespace SniLib {
    internal static class Utilities {
        internal static string HashSha256(this string text) {
            var textBytes = Encoding.UTF8.GetBytes(text);
            var textSha256 = SHA256.Create().ComputeHash(textBytes);
            return Convert.ToBase64String(textSha256);
        }

        internal static string HashPwd(this string password) {
            var pwdSha256 = HashSha256(password);
            return BCrypt.Net.BCrypt.HashPassword(pwdSha256);
        }

        internal static bool CheckPwd(this string pwdHashed, string password) {
            var pwdSha256 = HashSha256(password);
            return BCrypt.Net.BCrypt.Verify(pwdSha256, pwdHashed);
        }

        internal static T DoNothing<T>(this T obj) {
            // 这个函数只是用来手动调整格式
            // 希望编译器会优化掉这个函数
            return obj;
        }
    }

    internal static class ToDictHelper {
        internal static Dictionary<string, object> ToDict(this object obj, bool nullable = false) {
            const BindingFlags bindingFlags = BindingFlags.Public | BindingFlags.Instance;
            return obj.GetType().GetProperties(bindingFlags)
                .Where(propertyInfo => nullable || propertyInfo.GetValue(obj, null) != null)
                .ToDictionary(property => property.Name, property => property.GetValue(obj, null));
        }
    }


    internal static class UserUtilities {
        internal static bool CheckUser(this Database database, Guid sessionId) {
            var user = database.UserService.GetBySessionId(sessionId);
            return user == null;
        }

        internal static bool CheckAdmin(this Guid sessionId) {
        }

        internal static bool CheckReader(this Guid sessionId) {
            return sessionId.CheckUser();
        }
    }
}
