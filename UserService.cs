using System;
using ServiceStack.OrmLite;

namespace SniLib {
    public class UserService : Service {
        public UserService(Database database) : base(database) {
            // 继承 Service 类的构造函数
            // 使用 Database 对象初始化服务
        }

        public User SignUp(User user) {
            // 当注册一个用户时，直接传入一个对象
            // 该对象应当具有所有逻辑上应有的属性
            // 这个函数将其插入数据库，然后返回它
            user.SessionId = Guid.NewGuid();
            user.Password = user.Password.HashPwd();
            var userId = this.connection.Insert(user);
            return this.connection.SingleById<User>(userId);
        }

        public Guid SignIn(string username, string password) {
            // 当登入一个用户时，只需传入用户名和密码
            // 这个函数将返回对应的用户的 SessionId
            var user = this.GetByUsername(username);
            if (!user.Password.CheckPwd(password)) {
                // 当用户名和密码不匹配时
                // 返回空的 SessionId
                return Guid.Empty;
            }
            user.SessionId = Guid.NewGuid();
            this.connection.Update(user);
            return user.SessionId;
        }

        public void SignOut(Guid sessionId) {
            // 当登出一个会话时，传入 SessionId
            // 这个函数将生成一个新的 SessionId
            // 这也就注销了之前的 SessionId
            var user = this.GetBySessionId(sessionId);
            user.SessionId = Guid.NewGuid();
            this.connection.Update(user);
        }

        public User GetUser(Guid sessionId) {
            // 根据 SessionId 获取对应的 User 对象
            // 这个函数是 GetBySessionId 函数的别名
            return this.GetBySessionId(sessionId);
        }

        public void SetUser(Guid sessionId, User user) {
            // 首先根据 SessionId 获取对应的用户
            // 然后根据传入的 User 对象更新这个用户
            var userOld = this.GetBySessionId(sessionId);
            userOld.Nickname = user.Nickname;         // 昵称
            userOld.FirstName = user.FirstName;       // 名字
            userOld.LastName = user.LastName;         // 姓氏
            userOld.EmailAddress = user.EmailAddress; // 邮箱
            userOld.PhoneNumber = user.PhoneNumber;   // 手机号
            this.connection.Update(userOld);
        }

        public void DeleteUser(Guid sessionId) {
        }

        public User GetByUserId(int userId) {
            return this.connection.SingleById<User>(userId);
        }

        public User GetBySessionId(Guid sessionId) {
            return this.connection.Single<User>(x => x.SessionId == sessionId);
        }

        public User GetByUsername(string username) {
            return this.connection.Single<User>(x => x.Username == username);
        }
    }
}
