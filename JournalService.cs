using System;
using ServiceStack.OrmLite;

namespace SniLib {
    public class JournalService : Service {
        public JournalService(Database database) : base(database) {
            // 继承 Service 类的构造函数
            // 使用 Database 对象初始化服务
        }

        public Journal AddJournal(Guid sessionId, Journal journal) {
            var user = this.database.UserService.GetBySessionId(sessionId);
        }

        public void SetJournal(Guid sessionId, Journal journal) {
        }

        public void DeleteJournal(Guid sessionId, int journalId) {
        }

        internal Journal GetByJournalId(int journalId) {
            // 对于主键，使用 SingleById 方法唯一确定一个对象
            return this.connection.SingleById<Journal>(journalId);
        }

        internal Journal GetByName(string name) {
            // 对于 Unique 字段，使用 Single 方法唯一确定一个对象
            return this.connection.Single<Journal>(x => x.Name == name);
        }

        internal Journal GetByIssn(string issn) {
            // 对于 Unique 字段，使用 Single 方法唯一确定一个对象
            return this.connection.Single<Journal>(x => x.Issn == issn);
        }

        internal Journal GetByCn(string cn) {
            // 对于 Unique 字段，使用 Single 方法唯一确定一个对象
            return this.connection.Single<Journal>(x => x.Cn == cn);
        }

        internal Journal GetByPdc(string pdc) {
            // 对于 Unique 字段，使用 Single 方法唯一确定一个对象
            return this.connection.Single<Journal>(x => x.Pdc == pdc);
        }
    }
}
