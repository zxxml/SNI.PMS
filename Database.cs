namespace SNI
{
    using System;
    using System.Collections.Generic;
    using System.Data;
    using BCrypt.Net;
    using ServiceStack;
    using ServiceStack.OrmLite;

    public class Database
    {
        public IDbConnection Connection { get; set; }

        public void BindSqlite(string filename = ":memory:")
        {
            var factory = new OrmLiteConnectionFactory(null, SqliteDialect.Provider);
            this.Connection = factory.OpenDbConnectionString(filename);
        }

        public void GenerateMapping()
        {
            this.Connection.CreateTableIfNotExists<User>();
            this.Connection.CreateTableIfNotExists<Journal>();
            this.Connection.CreateTableIfNotExists<Subscription>();
            this.Connection.CreateTableIfNotExists<Storage>();
            this.Connection.CreateTableIfNotExists<Article>();
            this.Connection.CreateTableIfNotExists<Borrowing>();
        }

        public Guid SignUp(User user)
        {
            var finalUser = new User
                                {
                                    Username = user.Username,
                                    Nickname = user.Nickname,
                                    Password = BCrypt.HashPassword(user.Password),
                                    FirstName = user.FirstName,
                                    LastName = user.LastName,
                                    EmailAddress = user.EmailAddress,
                                    PhoneNumber = user.PhoneNumber,
                                    Role = user.Role,
                                    SessionId = Guid.NewGuid()
                                };
            this.Connection.Save(finalUser, references: true);
            return finalUser.SessionId;
        }

        public Guid SignIn(User user)
        {
            var finalUser = this.Connection.Select<User>(x => x.Username == user.Username)[0];
            if (BCrypt.Verify(user.Password, finalUser.Password))
            {
                finalUser.SessionId = Guid.NewGuid();
                this.Connection.Save(finalUser, references: true);
                return finalUser.SessionId;
            }

            return Guid.Empty;
        }

        public User GetUser(Guid SessionId)
        {
            return this.Connection.Select<User>(x => x.SessionId == SessionId)[0];
        }

        public void SetUser(User user)
        {
            var finalUser = this.Connection.Select<User>(x => x.SessionId == user.SessionId)[0];
            user.Username = finalUser.Username;
            user.Password = finalUser.Password;
            this.Connection.Update(finalUser, user);
        }

        public void ChangePassword(Guid sessionId, string password)
        {
            var finalUser = this.Connection.Select<User>(x => x.SessionId == sessionId)[0];
            finalUser.Password = BCrypt.HashPassword(password);
            this.Connection.Save(finalUser);
        }
    }
}