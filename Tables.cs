namespace SNI
{
    using System;
    using ServiceStack.DataAnnotations;

    public enum Role
    {
        Admin, // 管理员
        Reader // 读者
    }

    public enum Frequency
    {
        Annually,     // 年刊
        Semiannually, // 半年刊
        Quarterly,    // 季刊
        Monthly,      // 月刊
        Semimonthly,  // 半月刊
        Fortnightly,  // 旬刊
        Weekly        // 周刊
    }

    public class User
    {
        [PrimaryKey] [AutoIncrement] public int UserId { get; set; }
        [Required] [Unique] public Guid SessionId { get; set; }
        [Required] [Unique] public string Username { get; set; } // 用户名
        [Required] public string Nickname { get; set; }          // 昵称
        [Required] public string Password { get; set; }          // 密码
        [Required] public Role Role { get; set; }                // 角色
        [Required] public string FirstName { get; set; }         // 名字
        [Required] public string LastName { get; set; }          // 姓氏
        [Required] public string EmailAddress { get; set; }      // 邮箱
        [Required] public string PhoneNumber { get; set; }       // 手机号
    }

    public class Journal
    {
        [PrimaryKey] [AutoIncrement] public int JournalId { get; set; }
        [Required] public string Name { get; set; }          // 期刊名称
        [Required] public string UsedName { get; set; }      // 曾用名
        [Required] public string Language { get; set; }      // 语种
        [Required] public Frequency Frequency { get; set; }  // 出版周期
        [Required] [Unique] public string Issn { get; set; } // ISSN 刊号
        [Required] [Unique] public string Cn { get; set; }   // CN 刊号
        [Required] [Unique] public string Pdc { get; set; }  // 邮发代号
        [Required] public string History { get; set; }       // 创刊时间
        [Required] public string Organizer { get; set; }     // 主办单位
        [Required] public string Publisher { get; set; }     // 出版单位
        [Required] public string Address { get; set; }       // 汇款地址
    }

    public class Subscription
    {
        [PrimaryKey] [AutoIncrement] public int SubscriptionId { get; set; }
        [Required] public int JournalId { get; set; } // 期刊 ID
        [Required] public int Year { get; set; }      // 征订年份
    }

    public class Storage
    {
        [PrimaryKey] [AutoIncrement] public int StorageId { get; set; }
        [Required] public int JournalId { get; set; } // 期刊 ID
        [Required] public int Year { get; set; }      // 年
        [Required] public int Volume { get; set; }    // 卷
        [Required] public int Issue { get; set; }     // 期
    }

    public class Article
    {
        [PrimaryKey] [AutoIncrement] public int ArticleId { get; set; }
        [Required] public int StorageId { get; set; }   // 库存 ID
        [Required] public int PageNumber { get; set; }  // 页码
        [Required] public string Title { get; set; }    // 标题
        [Required] public string Author { get; set; }   // 作者
        [Required] public string Content { get; set; }  // 内容
        [Required] public string Keyword1 { get; set; } // 关键字
        [Required] public string Keyword2 { get; set; }
        [Required] public string Keyword3 { get; set; }
        [Required] public string Keyword4 { get; set; }
        [Required] public string Keyword5 { get; set; }
    }

    public class Borrowing
    {
        [PrimaryKey] [AutoIncrement] public int BorrowingId { get; set; }
        [Required] public int UserId { get; set; }          // 用户 ID
        [Required] public int StorageId { get; set; }       // 库存 ID
        [Required] public DateTime BorrowTime { get; set; } // 借出时间
        [Required] public DateTime AgreedTime { get; set; } // 应还时间
        public DateTime ReturnTime { get; set; }            // 归还时间
    }
}