using System;

namespace FoodApp
{
    /// <summary>
    /// Represents a customer whose identity and shipping address were persisted from the checkout form.
    /// </summary>
    public class Customer
    {
        /// <summary>Gets or sets the auto-incremented primary key.</summary>
        public int Id { get; set; }

        /// <summary>Gets or sets the customer name.</summary>
        public string Name { get; set; }

        /// <summary>Gets or sets the customer email address.</summary>
        public string Email { get; set; }

        /// <summary>Gets or sets the customer phone number.</summary>
        public string Phone { get; set; }

        /// <summary>Gets or sets the shipping street.</summary>
        public string Street { get; set; }

        /// <summary>Gets or sets the shipping city.</summary>
        public string City { get; set; }

        /// <summary>Gets or sets the shipping country.</summary>
        public string Country { get; set; }

        /// <summary>Gets or sets the shipping zip code.</summary>
        public string ZipCode { get; set; }

        /// <summary>Gets or sets the UTC timestamp assigned when the record is saved.</summary>
        public DateTime CreatedAt { get; set; }
    }
}
