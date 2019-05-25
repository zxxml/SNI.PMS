using System.Data;

namespace SniLib {
    public class Service {
        protected readonly Database database;
        protected readonly IDbConnection connection;

        protected Service(Database database) {
            // 使用 Database 对象初始化服务
            this.database = database;
            this.connection = database.Connection;
        }
    }
}
