namespace SniLib {
    using System.Data;
    using ServiceStack.OrmLite;

    public class Database {
        public IDbConnection Connection { get; set; }
        public UserService UserService { get; set; }

        public Database(string filename = ":memory:") {
            this.BindSqlite(filename);
            this.GenerateMapping();
            this.BindServices();
        }

        public void BindSqlite(string filename) {
            var factory = new OrmLiteConnectionFactory(null, SqliteDialect.Provider);
            this.Connection = factory.OpenDbConnectionString(filename);
        }

        public void GenerateMapping() {
            this.Connection.CreateTableIfNotExists<User>();
            this.Connection.CreateTableIfNotExists<Journal>();
            this.Connection.CreateTableIfNotExists<Subscription>();
            this.Connection.CreateTableIfNotExists<Storage>();
            this.Connection.CreateTableIfNotExists<Article>();
            this.Connection.CreateTableIfNotExists<Borrowing>();
        }

        public void BindServices() {
            this.UserService = new UserService(this);
        }
    }
}
